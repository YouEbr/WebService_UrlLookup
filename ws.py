####################################################
# Web Service to satisfy url lookups
####################################################
import flask
import mariadb
from Utility.DB_Config_Loader import read_conf
import re
import waitress


app = flask.Flask(__name__)
DatabaseName = None
TableName = None
ColumnName = None
ConnectionInfo = None
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

# Landing/default page
@app.route('/', methods=['GET'])
def home():
    try:
        with open('page.html', 'r') as f:
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

    malware, msg = check_reputation(url=host_and_port)
    if malware is None:
        result = create_result(error=True, malware=None, url=host_and_port, msg=msg)
        return result, 404

    result = create_result(error=False, malware=malware, url=host_and_port, msg=msg)
    return result, 200


# Handles urls like:
#       http://127.0.0.1:5000/urlinfo/1?url=www.google.com
@app.route('/urlinfo/1', methods=['GET'])
def urlinfo_query_str():
    if 'url' in flask.request.args:
        url = flask.request.args.get('url')
        print("url= " + url)
        if url:
            malware, msg = check_reputation(url=url)
            if malware is None:
                result = create_result(error=True, malware=None, url=url, msg=msg)
                return result, 404

            result = create_result(error=False, malware=malware, url=url, msg=msg)
            return result, 200
        else:
            result = create_result(error=True, malware=None, url=url, msg=url_missing)
            return result, 404
    return page_not_found(None)


# To provide help/usage! Useful if landing page (/) goes bananas.
@app.route('/help', methods=['GET'])
def usage():
    result = create_result(error=False, malware=None, url="", msg=help_msg)
    return result, 200


@app.errorhandler(404)
def page_not_found(e):
    print("page_not_found")
    result = create_result(error=True, malware=None, url="", msg=resource_not_found)
    return result, 404


# Is URL malware?
# Returns True/False/None and a message. None is used when error happens.
def check_reputation(url):
    print(f"Checking the reputation of {url}")
    foundIt = False
    msg = ""

    host = get_host(url)
    if not host:
        return None, url_invalid

    print("Checking {} against DB".format(host))

    try:
        with mariadb.connect(database=DatabaseName, **ConnectionInfo) as conn:
            cursor = conn.cursor()
            sql = '''SELECT * FROM {} WHERE {}=?'''.format(TableName, ColumnName)
            cursor.execute(sql, (host,))
            for row in cursor:
                foundIt = True
                print(f"Found {row[0]} in {TableName} table of {DatabaseName} database.")

            if not foundIt:
                print(f"{url} was not found in any of DBs.")

    except Exception as err:
        print(err)
        foundIt = None
        msg = err.__str__()

    if foundIt is not None:
        if not foundIt:  # it is NOT malware
            msg = url_safe_msg
        else:
            msg = url_unsafe_msg

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
    try:
        with mariadb.connect(database=DatabaseName, **ConnectionInfo) as conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT COUNT(*) FROM {}""".format(TableName))
            print("{} urls exists in {} table of {} database".format(cursor.fetchall()[0][0], TableName,
                                                                     DatabaseName))
    except Exception as err:
        print(err)
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

    regex = r'^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})(:\d*)?([\/\w \.-]*)*\/?$'
    match = re.search(regex, url)

    if match:
        if match.group(2) is not None:
            domain = match.group(2).lstrip(r'www\d?.')
        if match.group(3) is not None:
            com = match.group(3)
        host = "{0}.{1}".format(domain, com)
        return host
    else:
        return None


def main(argv):
    check_and_setup()
    if argv == "prod":  # production
        app.config["DEBUG"] = False
        app.config["ENV"] = "production"
        waitress.serve(app, host='0.0.0.0', port=5000)
    else:                    # development - Default
        app.config["DEBUG"] = True
        app.config["ENV"] = "development"
        app.run(host='localhost', port=5000)


if __name__ == '__main__':
    main(None)
