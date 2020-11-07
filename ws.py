####################################################
# Web Service to satisfy url lookups
####################################################
import os
import flask
import mariadb
from Utility.DB_Config_Loader import read_conf
import re
import waitress
from time import sleep

app = flask.Flask(__name__)
DatabaseName = None
TableName = None
ColumnName = None
ConnectionInfo = None
home_page = "page.html"
url_safe_msg = "Url is safe"
url_unsafe_msg = "Url is NOT safe"
url_invalid = "Invalid URL was entered"
url_missing = "url is not provided. Try /help"
resource_not_found = "The resource could not be found. Try /help"
help_msg = "Welcome to UrlLookup webservice." \
           "Construct a GET request similar to any of the followings:" \
           "(i) http://127.0.0.1:5000/urlinfo/1/www.google.com:80/index.hmtl " \
           "(ii) http://127.0.0.1:5000/urlinfo/1/www.google.com:80 " \
           "(iii) http://127.0.0.1:5000/urlinfo/1?url=www.google.com "
default_page_error_msg = "<h1>Error occurred while opening default/test page. Add \"/help\"" \
                         " to the url for some help.</h1>"
MAX_RETRIES_NUM = 15


# Landing/default page
@app.route('/', methods=['GET'])
def home():
    try:
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), home_page)
        with open(file_path, 'r') as f:
            page = f.read()
            return page, 200
    except:
        return default_page_error_msg, 500


# Handles urls like:
#       http://127.0.0.1:5000/urlinfo/1/www.google.com:80/index.hmtl
#       http://127.0.0.1:5000/urlinfo/1/www.google.com:80
@app.route('/urlinfo/1/<host_and_port>/<orig_path_and_query_str>', methods=['GET'])
@app.route('/urlinfo/1/<host_and_port>', methods=['GET'])
def urlinfo_query_param(host_and_port, orig_path_and_query_str=None):
    if orig_path_and_query_str:
        print("hostname_and_port= " + host_and_port)
    if orig_path_and_query_str:
        print("original_path_and_query_string:" + orig_path_and_query_str)

    return urlinfo(url=host_and_port)


# Handles urls like:
#       http://127.0.0.1:5000/urlinfo/1?url=www.google.com
@app.route('/urlinfo/1', methods=['GET'])
def urlinfo_query_str():
    if 'url' in flask.request.args:
        url = flask.request.args.get('url')

        return urlinfo(url=url)

    return page_not_found(None)


# To provide help/usage! Useful if landing page (/) goes bananas.
@app.route('/help', methods=['GET'])
def usage():
    result = create_result(error=False, malware=None, url="", msg=help_msg)
    return result, 200


@app.errorhandler(404)
def page_not_found(e):
    print(resource_not_found)
    result = create_result(error=True, malware=None, url="", msg=resource_not_found)
    return result, 404


def urlinfo(url):
    malware, msg = check_reputation(url=url)
    if malware is None:
        result = create_result(error=True, malware=None, url=url, msg=msg)
        return result, 404

    result = create_result(error=False, malware=malware, url=url, msg=msg)
    return result, 200


# Is URL malware?
# Returns True/False/None and a message. None is used when error happens.
def check_reputation(url):
    print(f"Checking the reputation of {url}")
    foundIt = False
    msg = ""

    if not url:  # blank url!
        print(url_missing)
        return None, url_missing

    host = get_host(url)
    if not host:
        print(url_invalid)
        return None, url_invalid

    successful_connection = False
    retry_num = 1
    while (not successful_connection) and (retry_num < MAX_RETRIES_NUM):
        try:
            with mariadb.connect(database=DatabaseName, **ConnectionInfo) as conn:
                successful_connection = True
                cursor = conn.cursor()
                sql = '''SELECT * FROM {} WHERE {}=?'''.format(TableName, ColumnName)
                cursor.execute(sql, (host,))
                for row in cursor:
                    foundIt = True
                    print(f"Found {row[0]} in {TableName} table of {DatabaseName} database.")

                if not foundIt:
                    print(f"{url} was not found in any of DBs.")

        except mariadb.Error as err:
            if "Can't connect to" in str(err):
                print(err)
                print("Sleeping for 1 seconds before retrying...")
                sleep(1)
                retry_num += 1

    if retry_num == MAX_RETRIES_NUM:
        msg = "Could not connect to database server. Not trying any more.."
        print(msg)
        foundIt = None

    if foundIt is not None:
        if not foundIt:  # it is NOT malware
            msg = url_safe_msg
        else:
            msg = url_unsafe_msg
        print(msg)

    return foundIt, msg


# Sets the values of "result" dictionary
def create_result(error, malware, url, msg):
    result = {'url': url, 'error': error, 'malware': malware, 'message': msg}
    return result


# checks config and DB connection prior to running the service.
def check_and_setup():
    # Can I read from config? It exits if encountered any issues. Hence no need to use try:
    global DatabaseName, TableName, ColumnName, ConnectionInfo
    DatabaseName, TableName, ColumnName, ConnectionInfo = read_conf()

    # Can I access and read from DB?
    successful_connection = False
    retry_num = 1
    while (not successful_connection) and (retry_num < MAX_RETRIES_NUM):
        try:
            with mariadb.connect(database=DatabaseName, **ConnectionInfo) as conn:
                successful_connection = True
                cursor = conn.cursor()
                cursor.execute("""SELECT COUNT(*) FROM {}""".format(TableName))
                print("{} urls exists in {} table of {} database".format(cursor.fetchall()[0][0], TableName,
                                                                         DatabaseName))
        except mariadb.Error as err:
            if "Can't connect to" in str(err):
                print(err)
                print("Sleeping for 1 seconds before retrying...")
                sleep(1)
                retry_num += 1

    if retry_num == MAX_RETRIES_NUM:
        print("Could not connect to database server. Exiting...")
        exit(-1)


# Extracts the host from passed in URL
def get_host(url):
    # For any of the following urls, it returns google.com
    # "http://www.google.com:443/about"
    # "https://www.google.com"
    # "http://www.google.com/about"
    # "www.google.com:443/about"
    # "www.google.com
    # "google.com"

    regex = r'^(https?:\/\/)?(w*\d*\.)?([\da-z\.-]+)\.([a-z\.]{2,6})(:\d*)?([\/\w \.-]*)*\/?$'
    _url = url.lower()
    match = re.search(regex, _url)
    if match is None: return None
    if match.group(3) is None or match.group(4) is None: return None
    host = match.group(3) + "." + match.group(4)
    return host


def main(argv):
    check_and_setup()
    if argv == "prod":  # production
        app.config["DEBUG"] = False
        app.config["ENV"] = "production"
        waitress.serve(app, host='0.0.0.0', port=5000)
    else:  # development - Default
        app.config["DEBUG"] = True
        app.config["ENV"] = "development"
        app.run(host='localhost', port=5000)


if __name__ == '__main__':
    main(None)
