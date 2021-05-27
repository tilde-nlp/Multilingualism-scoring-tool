import sys
import json
import logging
import time
from pathlib import Path

import signal
import tornado.ioloop
import tornado.web
from twisted.internet import reactor
from mimetypes import guess_type

from urllib.parse import urlparse
import configparser
# pip install scrapy # Use version 2.4.0 # https://github.com/scrapy/scrapy/blob/master/LICENSE
from scrapy.utils.project import get_project_settings

from modules.scoring_tool import ScoringTool
from modules.scoring_tool import *
from modules.common_functions import is_ok_job_name

class ScoringHandler(tornado.web.RequestHandler):
    def initialize(self, scorer):
        self.scorer = scorer
        self.logger = logging.getLogger("ScoringHandler")

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET')

    def get(self):
        q = self.get_query_argument("q", "", False)
        if q == "download_results":
            local_file = self.scorer.save_results_as(self.scorer.jobtitle)
            # save_results_as(title_of_datajob)
            content_type, _ = guess_type(local_file)
            self.logger.debug(f"Saved file content type is {content_type}")
            self.add_header('Content-Type', content_type)
            self.add_header('Content-Disposition', f'attachment; filename="{Path(local_file).name}"') 
            with open(local_file) as source_file:
                self.write(source_file.read())
        else:
            with open("index.html", "r", encoding='utf-8') as htmlf:
                html = htmlf.read()
                self.write(html)


    def post(self):
        q = self.get_query_argument("q", "", False)

        if q == "start_crawl":
            self.logger.debug(f"Server received start_crawl request")
            urls = self.get_body_argument("urls", default=None, strip=False)
            hops = self.get_body_argument("hops", default=None, strip=False)
            jobtitle = self.get_body_argument("titleOfJob", default="crawljob", strip=False)
            urls = urls.split("\n")
            hops = int(hops)

            response = self.scorer.start_crawl(urls, hops, jobtitle)
            # Status message, about crawling started
            self.write(json.dumps(response, indent=2, ensure_ascii=False))
        elif q == "get_crawl_progress_status":
            self.logger.debug(f"Server received get_crawl_progress_status request")
            response = self.scorer.get_crawl_progress_status()
            self.write(json.dumps(response, indent=2, ensure_ascii=False))
        elif q == "get_current_scores":
            self.logger.debug(f"Server received get_current_scores request")
            response = self.scorer.get_current_stats()
            self.write(json.dumps(response, indent=2, ensure_ascii=False))
        elif q == "stop_crawl":
            self.logger.debug(f"Server received stop_crawl request")
            response = self.scorer.stop_crawl()
            self.write(json.dumps(response, indent=2, ensure_ascii=False))
        elif q == "quit":
            self.write(json.dumps("Exiting", indent=2, ensure_ascii=False))
            self.logger.debug(f"Server received quit request")
            try:
                reactor.stop()
            except Exception as e:
                self.logger.error(e)
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
    logging.debug(f"Server received CTRL+C signal")
    tornado.ioloop.IOLoop.instance().stop()


def run_scoring_web():
    config = configparser.ConfigParser(interpolation=None)
    config.read('settings.ini')

    report_config = configparser.ConfigParser(interpolation=None)
    report_config.read('report_settings.ini')

    PORT = '8989'
    ADDRESS = '127.0.0.127'
    
    # logging.basicConfig(
    #     filename = config.get('app', 'LOG_FILE', fallback='app.log'),
    #     encoding = config.get('app', 'LOG_ENCODING', fallback='utf-8'),
    #     format = config.get('app', 'LOG_FORMAT', fallback='%(asctime)s %(message)s'),
    #     datefmt = config.get('app', 'LOG_DATEFORMAT', fallback='%H:%M:%S'),
    #     level=getattr(logging, config.get('app', 'LOG_LEVEL', fallback='ERROR').upper()),
    #     filemode='w',
    # )
    # logger = logging.getLogger("app")
    logging.debug("App logger started")
    # logger.log(logging.DEBUG, "App logger started")

    scorer = ScoringTool(config, report_config)

    app = make_app(scorer)

    # app.listen(PORT, address = ADDRESS)
    app.listen(PORT)
    signal.signal(signal.SIGINT, sig_exit)
    # logger.debug(f"Server started on {PORT} port!")
    logging.debug(f"Server started on {PORT} port!")
    # print(f"Server started on {ADDRESS}:{PORT}!")
    print(f"Server started on {PORT} port!")
    tornado.ioloop.IOLoop.current().start()




sample_urls = [
    'https://www.bmw.com/',  # quite mulitlingual
    'https://www.memorywater.com/', # 19 links l2, 3 langs 
    'https://www.tilde.lv/',    # mulitlingual .ee .lt
    'http://gorny.edu.pl/', # 5 links l2, mono
    'https://www.norden.org/',
    'https://europa.eu/',
    'https://globalvoices.org/',
    'https://www.royalfloraholland.com',
    'https://luxexpress.com',
    'https://aerodium.technology',
    'https://www.madaracosmetics.com',
    'https://www.airbaltic.com',
    'https://census.gov.uk/help/languages-and-accessibility/languages',
]

def run_scoring(urls=sample_urls, hops=1):
    if urls == None:
        return 0
    config = configparser.ConfigParser(interpolation=None)
    config.read('settings.ini')
    report_config = configparser.ConfigParser(interpolation=None)
    report_config.read('report_settings.ini')
    
    scorer = ScoringTool(config, report_config)
    response = scorer.start_crawl(urls, hops)
    while response['status'] == "crawling":
        time.sleep(10)
        response = scorer.get_crawl_progress_status()
    response = scorer.stop_crawl()
    response = scorer.get_current_stats()
    sys.exit()



if __name__ == "__main__":
    # import argparse
    # parser = argparse.ArgumentParser(description='This is tool for evaluation of website multilinguality!')
    # parser.add_argument('-u', '--urls', nargs='+', help='Starting urls to evaluate, domains will be extracted from them.')
    # parser.add_argument('-p', '--port', default='8989', help='port.')
    # args = parser.parse_args()
    # urls = args.urls
    # run_scoring(urls)
    run_scoring_web()
