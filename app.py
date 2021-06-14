import sys
import json
import logging
from pathlib import Path

import signal
import tornado.ioloop
import tornado.web
from twisted.internet import reactor
from mimetypes import guess_type

import configparser
# pip install scrapy # Use version 2.4.0 # https://github.com/scrapy/scrapy/blob/master/LICENSE
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging

from modules.scoring_tool import ScoringTool
from modules.common_functions import is_ok_job_name


class ScoringHandler(tornado.web.RequestHandler):
    def initialize(self, scorer):
        self.scorer = scorer
        self.logger = logging.getLogger("ScoringHandler")
        self.stats_to_display = [
            'LDI_pages',
            'LDI_words',
            'language_balance',
            'language_balance_primary',     # 'language_balance24',
            'language_balance_extended',    # 'language_balance26',
            'covered_extended',
        ]


    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET')


    def get(self):
        q = self.get_query_argument("q", "", False)
        if q == "download_results":
            local_file = self.scorer.save_results_as_csv(self.stats_to_display)
            content_type, _ = guess_type(local_file)
            self.logger.debug(f"Saved file content type is {content_type}")
            self.add_header('Content-Type', content_type)
            self.add_header('Content-Disposition', f'attachment; filename="{Path(local_file).name}"') 
            with open(local_file) as source_file:
                self.write(source_file.read())
        elif q == "download_detailed_results":
            # local_file = self.scorer.save_results_as_json()
            local_file = self.scorer.save_results_as_full_csv()
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
            self.logger.debug(self.request)
            self.logger.debug(self.request.files)

            if self.request.files:
                self.logger.debug("There is urlFile",self.request.files['input_file'][0]['filename'])
                filecontent = self.request.files['input_file'][0]['body']
                urls = filecontent.decode("utf-8") 
            else:
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
        elif q == "list_previous_jobs":
            self.logger.debug(f"Server received list_previous_jobs request")
        elif q == "view_job_scores":
            job_id = self.get_body_argument("job_id", default=None, strip=False)
            self.logger.debug(f"Server received view_job_scores request for {job_id}")
        elif q == "quit":
            self.write(json.dumps("Exiting", indent=2, ensure_ascii=False))
            self.logger.debug(f"Server received quit request")
            try:
                reactor.stop()
            except Exception as e:
                self.logger.debug(e)
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
    # Disable default Scrapy log settings.
    configure_logging(install_root_handler=False)

    rotating_file_log = logging.handlers.RotatingFileHandler(
            config.get('crawler', 'LOG_FILE', fallback='app.log'), 
            maxBytes=1024*1024, 
            backupCount=1,
        )
    rotating_file_log.setFormatter(logging.Formatter(
            config.get('crawler', 'LOG_FORMAT', fallback='%(asctime)s %(message)s')
        ))
    rotating_file_log.setLevel(
            level=getattr(logging, config.get('crawler', 'LOG_LEVEL', fallback='ERROR').upper()),
        )
    logging.basicConfig(
            handlers = [rotating_file_log],
            format=config.get('crawler', 'LOG_FORMAT', fallback='%(asctime)s %(message)s'),
        )

    logger = logging.getLogger("app")
    logger.debug("App logger started")
    scorer = ScoringTool(config, report_config)

    app = make_app(scorer)

    app.listen(PORT)
    signal.signal(signal.SIGINT, sig_exit)
    logger.info(f"Server started on {PORT} port!")
    print(f"Server started on {PORT} port!")
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    run_scoring_web()
