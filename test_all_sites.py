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

        directory3 = OFFLINE_DIR + r'/www.tilde.lv'
        class Handler3(QuietHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=directory3, **kwargs)
        server_address3 = ('127.0.0.3', PORT)
        httpd3 = HTTPServer(server_address3, Handler3)
        start_server_in_separate_thread(httpd3)

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

        directory13 = OFFLINE_DIR + r'/census.gov.uk'
        class Handler13(QuietHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=directory13, **kwargs)
        server_address13 = ('127.0.0.13', PORT)
        httpd13 = HTTPServer(server_address13, Handler13)
        start_server_in_separate_thread(httpd13)


        urls = [
            f'http://127.0.0.3:{PORT}/', 
            f'http://127.0.0.5:{PORT}/', 
            f'http://127.0.0.6:{PORT}/',
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
        self.assertEqual(response['message'], "Started crawling of 4 urls.") 
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

        score, stats = response['127.0.0.3']
        self.assertEqual(score, '4.17') # monolingual - latvian

        score, stats = response['127.0.0.5']
        self.assertNotEqual(score, '0.00')
        score, stats = response['127.0.0.6']
        self.assertNotEqual(score, '0.00')
        score, stats = response['127.0.0.13']
        self.assertNotEqual(score, '0.00')

        httpd3.shutdown()
        httpd5.shutdown()
        httpd6.shutdown()
        httpd13.shutdown()

if __name__ == '__main__':
    unittest.main()