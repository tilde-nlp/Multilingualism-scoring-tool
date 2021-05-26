import unittest
from app import * 
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import time
# Automatically can test only one site on callback address, 
# because analysis is saved on per-domain basis
# (multiple sites on localhost will have the same "domain" - "localhost")
# and scrapy does not allow sequential runs (Twisted reactor cant be restarted)


class TestSpider(unittest.TestCase):
    def test_scoring(self):
        OFFLINE_DIR = r'./tests/offline_sites'
        PORT = 8000

        def serve_forever(httpd):
            httpd.serve_forever()

        # run HTTPServer on separate thread
        def start_server_in_separate_thread(httpd):
            thread = threading.Thread(target=serve_forever, args=(httpd, ))
            thread.setDaemon(True)
            thread.start()

        class QuietHandler(SimpleHTTPRequestHandler):
            # Dont flood console wiht http requests info
            def log_message(self, format, *args):
                pass

        directory = OFFLINE_DIR + r'/www.bmw.com'
        class Handler(QuietHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=directory, **kwargs)
        server_address = ('127.0.0.1', PORT)
        httpd = HTTPServer(server_address, Handler)
        start_server_in_separate_thread(httpd)

        directory2 = OFFLINE_DIR + r'/www.memorywater.com'
        class Handler2(QuietHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=directory2, **kwargs)
        server_address2 = ('127.0.0.2', PORT)
        httpd2 = HTTPServer(server_address2, Handler2)
        start_server_in_separate_thread(httpd2)

        directory3 = OFFLINE_DIR + r'/www.tilde.lv'
        class Handler3(QuietHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=directory3, **kwargs)
        server_address3 = ('127.0.0.3', PORT)
        httpd3 = HTTPServer(server_address3, Handler3)
        start_server_in_separate_thread(httpd3)

        directory4 = OFFLINE_DIR + r'/gorny.edu.pl'
        class Handler4(QuietHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=directory4, **kwargs)
        server_address4 = ('127.0.0.4', PORT)
        httpd4 = HTTPServer(server_address4, Handler4)
        start_server_in_separate_thread(httpd4)

        directory5 = OFFLINE_DIR + r'/www.norden.org'
        class Handler5(QuietHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=directory5, **kwargs)
        server_address5 = ('127.0.0.5', PORT)
        httpd5 = HTTPServer(server_address5, Handler5)
        start_server_in_separate_thread(httpd5)

        directory6 = OFFLINE_DIR + r'/europa.eu'
        class Handler6(QuietHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=directory6, **kwargs)
        server_address6 = ('127.0.0.6', PORT)
        httpd6 = HTTPServer(server_address6, Handler6)
        start_server_in_separate_thread(httpd6)

        directory7 = OFFLINE_DIR + r'/globalvoices.org'
        class Handler7(QuietHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=directory7, **kwargs)
        server_address7 = ('127.0.0.7', PORT)
        httpd7 = HTTPServer(server_address7, Handler7)
        start_server_in_separate_thread(httpd7)

        directory8 = OFFLINE_DIR + r'/www.royalfloraholland.com'
        class Handler8(QuietHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=directory8, **kwargs)
        server_address8 = ('127.0.0.8', PORT)
        httpd8 = HTTPServer(server_address8, Handler8)
        start_server_in_separate_thread(httpd8)

        directory9 = OFFLINE_DIR + r'/luxexpress.eu'
        class Handler9(QuietHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=directory9, **kwargs)
        server_address9 = ('127.0.0.9', PORT)
        httpd9 = HTTPServer(server_address9, Handler9)
        start_server_in_separate_thread(httpd9)

        directory10 = OFFLINE_DIR + r'/aerodium.technology'
        class Handler10(QuietHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=directory10, **kwargs)
        server_address10 = ('127.0.0.10', PORT)
        httpd10 = HTTPServer(server_address10, Handler10)
        start_server_in_separate_thread(httpd10)

        directory11 = OFFLINE_DIR + r'/www.madaracosmetics.com'
        class Handler11(QuietHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=directory11, **kwargs)
        server_address11 = ('127.0.0.11', PORT)
        httpd11 = HTTPServer(server_address11, Handler11)
        start_server_in_separate_thread(httpd11)

        directory12 = OFFLINE_DIR + r'/www.airbaltic.com'
        class Handler12(QuietHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=directory12, **kwargs)
        server_address12 = ('127.0.0.12', PORT)
        httpd12 = HTTPServer(server_address12, Handler12)
        start_server_in_separate_thread(httpd12)

        directory13 = OFFLINE_DIR + r'/census.gov.uk'
        class Handler13(QuietHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=directory13, **kwargs)
        server_address13 = ('127.0.0.13', PORT)
        httpd13 = HTTPServer(server_address13, Handler13)
        start_server_in_separate_thread(httpd13)


        urls = [
            f'http://127.0.0.1:{PORT}/', 
            f'http://127.0.0.2:{PORT}/', 
            f'http://127.0.0.3:{PORT}/', 
            f'http://127.0.0.4:{PORT}/',
            f'http://127.0.0.5:{PORT}/', 
            f'http://127.0.0.6:{PORT}/',
            f'http://127.0.0.7:{PORT}/', 
            f'http://127.0.0.8:{PORT}/',
            f'http://127.0.0.9:{PORT}/', 
            f'http://127.0.0.10:{PORT}/',
            f'http://127.0.0.11:{PORT}/', 
            f'http://127.0.0.12:{PORT}/',
            f'http://127.0.0.13:{PORT}/',
            ]
        config = configparser.ConfigParser(interpolation=None)
        config.read('settings.ini')
        config['crawler']['DOWNLOAD_DELAY'] = "0"
        report_config = configparser.ConfigParser(interpolation=None)
        report_config.read('report_settings.ini')

        from modules.scoring_tool import ScoringTool
        scorer = ScoringTool(config, report_config)
        
        response = scorer.start_crawl(urls, hops=1)
        self.assertEqual(response['status'], "crawling")
        self.assertEqual(response['message'], "Started crawling of 13 urls.") 
        response = scorer.start_crawl(urls, hops=1)
        self.assertEqual(response['status'], "error")
        self.assertEqual(response['message'], "Can not start, already crawling.") 

        time.sleep(10)
        response = scorer.get_crawl_progress_status()
        self.assertEqual(response['status'], "crawling")
        self.assertEqual(response['message'], "crawling") 
        time.sleep(10)

        response = scorer.stop_crawl()
        self.assertEqual(response['status'], "stopping")
        self.assertEqual(response['message'], "stopping") 
        time.sleep(10)  # Give time to stop process normally
        response = scorer.stop_crawl()
        if not response['status'] == "ready":
            time.sleep(10)
            response = scorer.stop_crawl()
        self.assertEqual(response['status'], "ready")
        self.assertEqual(response['message'], "ready") 

        response = scorer.get_current_stats()
        score, stats = response['127.0.0.4']
        self.assertEqual(score, '4.17') # 1 * 1 / 24 # pl balance 1/24 eu langs
        score, stats = response['127.0.0.5']
        self.assertNotEqual(score, '0.00')

        httpd.shutdown()
        httpd2.shutdown()
        httpd3.shutdown()
        httpd4.shutdown()
        httpd5.shutdown()
        httpd6.shutdown()
        httpd7.shutdown()
        httpd8.shutdown()
        httpd9.shutdown()
        httpd10.shutdown()
        httpd11.shutdown()
        httpd12.shutdown()
        httpd13.shutdown()

if __name__ == '__main__':
    unittest.main()