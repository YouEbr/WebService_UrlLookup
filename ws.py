####################################################
# Web Service to satisfy url lookups
####################################################
import flask
import random

app = flask.Flask(__name__)
app.config["DEBUG"] = True
# setting the result with default fields.
result = {'error': False, 'malware': False, 'message': "The resource could not be found.", 'url': ""}


# Landing/default page
@app.route('/', methods=['GET'])
def home():
    try:
        with open('page.html', 'r') as f:
            page = f.read()
            return page
    except:
        return "<h1>Error occurred while opening default/test page. Add \"/help\"" \
               " to the url for some help.</h1>"


# Handles urls like:
#       http://127.0.0.1:5000/urlinfo/1/www.google.com:80/index.hmtl
#       http://127.0.0.1:5000/urlinfo/1/www.google.com:80
@app.route('/urlinfo/1/<host_and_port>/<orig_path_and_query_str>', methods=['GET'])
@app.route('/urlinfo/1/<host_and_port>', methods=['GET'])
def urlinfo_1(host_and_port, orig_path_and_query_str=None):
    print("urlinfo_1")
    if orig_path_and_query_str:
        print("hostname_and_port= " + host_and_port)
    if orig_path_and_query_str:
        print("original_path_and_query_string:" + orig_path_and_query_str)

    malware = get_reputation(url=host_and_port)
    set_result_values(malware=malware, url=host_and_port)
    return result, 200


# Handles urls like:
#       http://127.0.0.1:5000/urlinfo/1?url=www.google.com
@app.route('/urlinfo/1', methods=['GET'])
def urlinfo_2():
    print("urlinfo_2")
    if 'url' in flask.request.args:
        url = flask.request.args.get('url')
        print("url= " + url)
        if url:
            malware = get_reputation(url=url)
            set_result_values(malware=malware, url=url)
            return result, 200
        else:
            set_result_values(malware=False, url=url)
            result['error'] = True
            result['message'] = "url is not provided. Try /help"
            return result, 404
    return page_not_found(None)


# To provide help/usage! Useful if landing page (/) goes bananas.
@app.route('/help', methods=['GET'])
def usage():
    result['message'] = "Welcome to UrlLookup webservice." \
                        "Construct a GET request similar to any of the followings:" \
                        "(i) http://127.0.0.1:5000/urlinfo/1/www.google.com:80/index.hmtl " \
                        "(ii) http://127.0.0.1:5000/urlinfo/1/www.google.com:80 " \
                        "(iii) http://127.0.0.1:5000/urlinfo/1?url=www.google.com "
    return result, 200


@app.errorhandler(404)
def page_not_found(e):
    print("page_not_found")
    result['error'] = True
    result['malware'] = False
    result['message'] = "The resource could not be found. Try /help"
    result['url'] = ""
    return result, 404


# Is URL malware?
# TODO: Implement the method. Right now it decides randomly! :-O
def get_reputation(url):
    k = random.randint(0, 1)
    if k == 0:
        return False
    return True


# Sets the values of "result" dictionary
def set_result_values(malware, url):
    result['url'] = url
    result['error'] = False
    if malware:
        result['malware'] = True
        result['message'] = "Url is NOT safe"
    else:
        result['malware'] = False
        result['message'] = "Url is safe"


if __name__ == '__main__':
    app.run()
