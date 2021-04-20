import unittest
from app import * 
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
# Automatically can test only one site on localhost, 
# because analysis is saved on per-domain basis
# (multiple sites on localhost will have the same "domain" - "localhost")
# and scrapy does not allow sequential runs (Twisted reactor cant be restarted)


class TestSpider(unittest.TestCase):
    def test_scoring_tilde(self):
        # OFFLINE_DIR = r'\scoring_tool\tests\offline_sites' 
        OFFLINE_DIR = r'.\tests\offline_sites' 
        directory = OFFLINE_DIR + r'\www.tilde.lv'
        PORT = 8000
        class Handler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=directory, **kwargs)

        # run HTTPServer on separate thread
        server_address = ('', PORT)
        httpd = HTTPServer(server_address, Handler)
        def serve_forever(httpd):
            httpd.serve_forever()
        thread = threading.Thread(target=serve_forever, args=(httpd, ))
        thread.setDaemon(True)
        thread.start()

        score = run_scoring([f'http://localhost:{PORT}/'])

        httpd.shutdown()

if __name__ == '__main__':
    unittest.main()