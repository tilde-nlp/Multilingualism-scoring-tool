import os
import shutil
import sys
import json
import threading
from multiprocessing import Process

import signal
import tornado.ioloop
import tornado.web
from twisted.internet import reactor

from urllib.parse import urlparse
import configparser
# pip install scrapy # Use version 2.4.0 # https://github.com/scrapy/scrapy/blob/master/LICENSE
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from modules.scoring_tool import ScoringTool

class ScoringHandler(tornado.web.RequestHandler):
    def initialize(self, scorer):
        self.scorer = scorer

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET')

    def get(self):
        with open("index.html", "r", encoding='utf-8') as htmlf:
            html = htmlf.read()
        self.write(html)


    def post(self):
        # API v.1
        #     start_crawl(urls, settings={hopi,})
        #         starts crawling of urls using settings
        #         returns "Started crawling of {len(urls)} urls."
        #     get_crawl_progress_status()
        #         ? return current depth of crawling for each url ?
        #     get_current_scores()
        #         returns statistics&scores at this moment
        #     stop_crawl()
        #         stops crawling and returns get_current_scores()
        q = self.get_query_argument("q", "", False)

        if q == "start_crawl":
            urls = self.get_body_argument("urls", default=None, strip=False)
            hops = self.get_body_argument("hops", default=None, strip=False)
            urls = urls.split("\n")
            hops = int(hops)

            response = self.scorer.start_crawl(urls, hops)
            # Status message, about crawling started
            self.write(json.dumps(response, indent=2, ensure_ascii=False))
        elif q == "get_crawl_progress_status":
            response = self.scorer.get_crawl_progress_status()
            self.write(json.dumps(response, indent=2, ensure_ascii=False))
        elif q == "get_current_scores":
            response = self.scorer.get_current_stats()
            self.write(json.dumps(response, indent=2, ensure_ascii=False))
        elif q == "stop_crawl":
            response = self.scorer.stop_crawl()
            self.write(json.dumps(response, indent=2, ensure_ascii=False))
        elif q == "quit":
            self.write(json.dumps("Exiting", indent=2, ensure_ascii=False))
            print("Exiting")
            reactor.stop()
            sys.exit()

def make_app(scorer):
    return tornado.web.Application([
        (r"/score", ScoringHandler, {"scorer": scorer}),
        (r"/images/(.*)", tornado.web.StaticFileHandler, {
            "path": "./images/"
        }),
    ])

def sig_exit(signum, frame):
    tornado.ioloop.IOLoop.instance().add_callback_from_signal(do_stop)

def do_stop():
    print("Trying to stop")
    tornado.ioloop.IOLoop.instance().stop()


def run_scoring_web():
    PORT = '8989'
    # ADDRESS = '127.0.0.127'

    scorer = ScoringTool()
    app = make_app(scorer)

    # app.listen(PORT, address = ADDRESS)
    app.listen(PORT)
    signal.signal(signal.SIGINT, sig_exit)
    # print(f"Server started on {ADDRESS}:{PORT}!")
    print(f"Server started on {PORT} port!")
    tornado.ioloop.IOLoop.current().start()


# def run_scoring(urls=None):
#     if urls == None:
#         urls = [
#             # 'https://www.bmw.com/',  # quite mulitlingual
#             # 'https://www.memorywater.com/', # 19 links l2, 3 langs 
#             # 'https://www.tilde.lv/',    # mulitlingual .ee .lt
#             'http://gorny.edu.pl/', # 5 links l2, mono
#             # 'https://www.norden.org/',
#             # 'https://europa.eu/',
#             # 'https://globalvoices.org/',
#             # 'https://www.royalfloraholland.com',
#             # 'https://luxexpress.com',
#             # 'https://aerodium.technology',
#             # 'https://www.madaracosmetics.com',
#             # 'https://www.airbaltic.com',
#             # 'https://census.gov.uk/help/languages-and-accessibility/languages',

#         ]

#     scorer = ScoringTool()
    
#     score = scorer.initialize(urls)

#     print("Done crawling ")
#     return score    # returns last score for testing


if __name__ == "__main__":
    # import argparse
    # parser = argparse.ArgumentParser(description='This is tool for evaluation of website multilinguality!')
    # parser.add_argument('-u', '--urls', nargs='+', help='Starting urls to evaluate, domains will be extracted from them.')
    # parser.add_argument('-p', '--port', default='8989', help='port.')
    # args = parser.parse_args()
    # urls = args.urls
    # run_scoring(urls)
    run_scoring_web()
