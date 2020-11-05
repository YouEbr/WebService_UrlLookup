import json
import unittest
import ws


class TestWebService(unittest.TestCase):

    def setUp(self):
        ws.check_and_setup()
        ws.app.testing = True
        self.client = ws.app.test_client()

    def tearDown(self):
        pass

    def test_get_host(self):
        self.assertEqual(ws.get_host("https://www.google.com:443"), "google.com")
        self.assertEqual(ws.get_host("http://www.google.com:443/about"), "google.com")
        self.assertEqual(ws.get_host("www.google.com:443/about"), "google.com")
        self.assertEqual(ws.get_host("google.com"), "google.com")
        self.assertEqual(ws.get_host("GOOGLE.COM"), "google.com")
        self.assertEqual(ws.get_host("97b1c56132dfcdd90f93-0c5c8388c0a5897e648f883e2c86dc72.r54.cf5.rackcdn.com"),
                         "97b1c56132dfcdd90f93-0c5c8388c0a5897e648f883e2c86dc72.r54.cf5.rackcdn.com")
        self.assertEqual(ws.get_host("www.url-with-dash.com"), "url-with-dash.com")
        self.assertEqual(ws.get_host("https://www3.w3school.com/python/ref_string_lstrip.asp"), "w3school.com")
        self.assertEqual(ws.get_host("https://wwwin.cisco.com/c/cec/employee.html"), "wwwin.cisco.com")
        self.assertEqual(ws.get_host("https://docs.python.org/3/library/re.html"), "docs.python.org")
        self.assertEqual(ws.get_host("www.d1054130-28095.cp.blacknight.com"), "d1054130-28095.cp.blacknight.com")
        self.assertEqual(ws.get_host("http:google.com"), None)
        self.assertEqual(ws.get_host("abc"), None)

    def test_check_reputation(self):
        self.assertEqual(ws.check_reputation("google.com"), (False, ws.url_safe_msg))
        self.assertEqual(ws.check_reputation("999fitness.com"), (True, ws.url_unsafe_msg))
        self.assertEqual(ws.check_reputation("abc")[0], None)

    def test_home(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        #  resp.status, resp.data, resp.content_type, resp.content_length  # https://tedboy.github.io/flask/generated/generated/flask.Response.html

    def test_help(self):
        resp = self.client.get('/help')
        resp_data = json.loads(resp.data)
        self.assertEqual((resp.status_code, resp_data['error'], resp_data['malware'], resp_data['message']), (200, False, None, ws.help_msg))


    def test_urlinfo_query_param(self):
        # testing couple of different url formats. All Safe (not malware)
        resp = self.client.get('http://127.0.0.1:5000/urlinfo/1/www.google.com:80/index.hmtl')
        resp_data = json.loads(resp.data)
        self.assertEqual((resp.status_code, resp_data['error'], resp_data['malware']), (200, False, False))

        resp = self.client.get('http://127.0.0.1:5000/urlinfo/1/www.google.com:80')
        resp_data = json.loads(resp.data)
        self.assertEqual((resp.status_code, resp_data['error'], resp_data['malware']), (200, False, False))

        resp = self.client.get('http://127.0.0.1:5000/urlinfo/1/www.google.com:443/about')
        resp_data = json.loads(resp.data)
        self.assertEqual((resp.status_code, resp_data['error'], resp_data['malware']), (200, False, False))

        # testing couple of malware urls
        resp = self.client.get(
            'http://127.0.0.1:5000/urlinfo/1/97b1c56132dfcdd90f93-0c5c8388c0a5897e648f883e2c86dc72.r54.cf5.rackcdn.com')
        resp_data = json.loads(resp.data)
        self.assertEqual((resp.status_code, resp_data['error'], resp_data['malware']), (200, False, True))

        resp = self.client.get('http://127.0.0.1:5000/urlinfo/1/www.amazon-sicherheit.kunden-ueberpruefung.xyz')
        resp_data = json.loads(resp.data)
        self.assertEqual((resp.status_code, resp_data['error'], resp_data['malware']), (200, False, True))

        resp = self.client.get('http://127.0.0.1:5000/urlinfo/1/www.d1054130-28095.cp.blacknight.com')
        resp_data = json.loads(resp.data)
        self.assertEqual((resp.status_code, resp_data['error'], resp_data['malware']), (200, False, True))

    def test_urlinfo_query_str(self):
        # testing couple of different url formats. All Safe (not malware)
        resp = self.client.get('http://127.0.0.1:5000/urlinfo/1?url=www.google.com:80/index.hmtl')
        resp_data = json.loads(resp.data)
        self.assertEqual((resp.status_code, resp_data['error'], resp_data['malware']), (200, False, False))

        resp = self.client.get('http://127.0.0.1:5000/urlinfo/1?url=www.google.com:80')
        resp_data = json.loads(resp.data)
        self.assertEqual((resp.status_code, resp_data['error'], resp_data['malware']), (200, False, False))

        resp = self.client.get('http://127.0.0.1:5000/urlinfo/1?url=www.google.com:443/about')
        resp_data = json.loads(resp.data)
        self.assertEqual((resp.status_code, resp_data['error'], resp_data['malware']), (200, False, False))

        # testing couple of malware urls
        resp = self.client.get(
            'http://127.0.0.1:5000/urlinfo/1?url=97b1c56132dfcdd90f93-0c5c8388c0a5897e648f883e2c86dc72.r54.cf5.rackcdn.com')
        resp_data = json.loads(resp.data)
        self.assertEqual((resp.status_code, resp_data['error'], resp_data['malware']), (200, False, True))

        resp = self.client.get('http://127.0.0.1:5000/urlinfo/1?url=www.amazon-sicherheit.kunden-ueberpruefung.xyz')
        resp_data = json.loads(resp.data)
        self.assertEqual((resp.status_code, resp_data['error'], resp_data['malware']), (200, False, True))

        resp = self.client.get('http://127.0.0.1:5000/urlinfo/1?url=www.d1054130-28095.cp.blacknight.com')
        resp_data = json.loads(resp.data)
        self.assertEqual((resp.status_code, resp_data['error'], resp_data['malware']), (200, False, True))



