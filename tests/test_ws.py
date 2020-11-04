import unittest
import ws


class TestWebService(unittest.TestCase):

    def setUp(self):
        ws.check_and_setup()

    def tearDown(self):
        pass

    def test_get_host(self):
        self.assertEqual(ws.get_host("https://www.google.com:443"), "google.com")
        self.assertEqual(ws.get_host("http://www.google.com:443/about"), "google.com")
        self.assertEqual(ws.get_host("www.google.com:443/about"), "google.com")
        self.assertEqual(ws.get_host("google.com"), "google.com")
        self.assertEqual(ws.get_host("97b1c56132dfcdd90f93-0c5c8388c0a5897e648f883e2c86dc72.r54.cf5.rackcdn.com"),
                         "97b1c56132dfcdd90f93-0c5c8388c0a5897e648f883e2c86dc72.r54.cf5.rackcdn.com")
        self.assertEqual(ws.get_host("http:google.com"), None)
        self.assertEqual(ws.get_host("abc"), None)

    def test_check_reputation(self):
        self.assertEqual(ws.check_reputation("google.com"), (False, ws.url_safe_msg))
        self.assertEqual(ws.check_reputation("999fitness.com"), (True, ws.url_unsafe_msg))
        self.assertEqual(ws.check_reputation("abc")[0], None)