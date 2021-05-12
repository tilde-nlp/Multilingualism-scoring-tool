import os
import shutil
import sys
# import threading
import logging
import time

from urllib.parse import urlparse
import configparser
# pip install scrapy # Use version 2.4.0 # https://github.com/scrapy/scrapy/blob/master/LICENSE
import scrapy
from scrapy.crawler import CrawlerProcess, CrawlerRunner, Crawler
from modules.spider import ScoringSpider
from modules.spider import ScoringSpiderSitemap
from modules.analyzer import Analyzer
from modules.reporter import Reporter
from modules.common_functions import extractDomain

from twisted.internet import reactor, defer

from scrapy.utils.project import get_project_settings

from multiprocessing import Process


class ScoringTool():
    def __init__(self, config):
        self.logger = logging.getLogger("ScoringTool")
        
        # settings = {}
        self.settings = get_project_settings()        

        self.config = config
        def override_default_crawler_config():
            for key in self.config['crawler']:
                self.settings[key.upper()] = self.config.get('crawler', key, fallback='')
        override_default_crawler_config()
        self.status = "ready" # ready, crawling, stopping, error 
        self.p = None


    def get_crawl_progress_status(self):
        try:
            crawlers = self.process.crawlers
            if len(crawlers) > 0 and self.status=="stopping":
                self.status = "stopping"
            elif len(crawlers) > 0:
                self.status = "crawling"
            else:
                self.status = "ready"
        except Exception as e:
            print(e)

        current_status = {}
        try:
            current_status["status"] = self.status
            current_status["message"] = self.status
        except AttributeError:
            current_status["status"] = "error" 
            current_status["message"] = "No stats - nothing to analyze. Maybe scoring tool not yet initialized?"
        return current_status


    def get_current_stats(self):
        current_status = {}
        try: 
            allowed_domains = self.allowed_domains
        except AttributeError:
            current_status["status"] = "error" 
            current_status["message"] = "No stats - nothing to analyze. Maybe scoring tool not yet initialized?"
            return current_status

        for domain in self.allowed_domains:
            try:
                stats = self.reporter.get_stats(domain)
            except Exception as e:
                self.logger.error(f"{e}")
            # stats: 'language_balance', 'lang_count', 'langs', # For full list see Reporter
            score = self.reporter.get_score_from_stats(stats)
            score = score * 100
            score = "{:0.2f}".format(score)
            print("Domain: {}, score: {}, langs: {}".format(domain, score, stats['langs']))
            current_status[domain] = (score, stats)
        # return (score, stats)
        return current_status
    

    def start_crawl(self, urls, hops):
        if self.status in ["crawling", "stopping"]:
            current_status = {}
            current_status["status"] = "error" 
            current_status["message"] = "Can not start, already crawling."
            return current_status
            
        self.urls = urls

        self.sitemap_urls = []
        for url in urls:
            parsed_url = urlparse(url)
            self.sitemap_urls.append(f'{parsed_url.scheme}://{parsed_url.netloc}/sitemap.xml')
            self.sitemap_urls.append(f'{parsed_url.scheme}://{parsed_url.netloc}/robots.txt')


        # override DEPTH_LIMIT with "hops" from UI
        self.settings['DEPTH_LIMIT'] = hops

        self.analyzer_data_dir = self.config.get('analyzer', 'data_dir', fallback='')
        self.reporter = Reporter(self.analyzer_data_dir)
        self.allowed_domains = [extractDomain(i) for i in urls]
        # print(f'\nPrepared allowed_domains {allowed_domains}\n')

        def dump_config_to_file_for_debug():
            with open('settings.cfg', 'w', encoding='utf-8') as of:
                for key, value in self.settings.items():
                    of.write(f'{key}, {value}\n')
        dump_config_to_file_for_debug()

        def clean_analyzed_dir_before_running():
            try:
                shutil.rmtree(self.analyzer_data_dir)
            except Exception as e:
                print("Exception "+str(e))
                pass
        clean_analyzed_dir_before_running()

        # Define spider(s)
        spider = ScoringSpider  # CrawlerProcess accepts Spider class or Crawler instances
        sitemapspider = ScoringSpiderSitemap
        spider.start_urls = self.urls
        spider.allowed_domains = self.allowed_domains 
        spider.analyzer = Analyzer(self.analyzer_data_dir)
        sitemapspider.allowed_domains = self.allowed_domains
        sitemapspider.sitemap_urls = self.sitemap_urls
        sitemapspider.analyzer = spider.analyzer    # the same as spider

        self.process = CrawlerProcess(settings=self.settings)
        self.process.crawl(sitemapspider)
        self.process.crawl(spider)
        # Similar approach:
        # https://stackoverflow.com/questions/11528739/running-scrapy-spiders-in-a-celery-task
        # threading VERY slow in Docker
        # threading.Thread(target=self.process.start, args=(False,)).start()
        self.p = Process(target=self.process.start, args=(False,))
        self.p.start()
        

        # https://stackoverflow.com/questions/14274916/execute-twisted-reactor-run-in-a-thread/14282640
        # self.process = CrawlerRunner(settings=self.settings)

        # spider = ScoringSpider  # CrawlerProcess accepts Spider class or Crawler instances
        # sitemapspider = ScoringSpiderSitemap

        # spider.start_urls = self.urls
        # spider.allowed_domains = self.allowed_domains 
        # spider.analyzer = Analyzer(self.analyzer_data_dir)
        # sitemapspider.allowed_domains = self.allowed_domains
        # sitemapspider.sitemap_urls = self.sitemap_urls
        # sitemapspider.analyzer = spider.analyzer

        # @defer.inlineCallbacks
        # def crawl():
        #     self.logger.debug(f"Crawling in twisted started.")
        #     yield self.process.crawl(sitemapspider)
        #     yield self.process.crawl(spider)
        #     # Actual crawl done
        #     print("Crawling in twisted done") 
        #     self.logger.debug(f"Crawling in twisted done.")
        #     self.process = None
        #     self.status = "ready"
        #     # reactor.stop()

        # crawl()

        # if not reactor.running:
        #     threading.Thread(target=reactor.run, args=(False,)).start()

        self.status = "crawling"

        current_status = {}
        current_status["status"] = self.status 
        current_status["message"] = f"Started crawling of {len(spider.start_urls)} urls."
        return current_status


    def stop_crawl(self):
        print("Stop command received")
        if self.status == "crawling":
            try:
                self.process.stop()
            except Exception as e:
                print(e)
            self.status = "stopping"
        elif self.status == "stopping":
            # Second time, force stop
            print("Second stop, killing p")
            self.p.terminate()
            time.sleep(0.1)
            if not self.p.is_alive():
                print("p is a goner")
                self.p.join(timeout=1.0)
                print("Joined p successfully!")
                self.status = "ready"

        current_status = {}
        try:
            current_status["status"] = self.status
            current_status["message"] = self.status
        except AttributeError:
            current_status["status"] = "error" 
            current_status["message"] = "No stats - nothing to analyze. Maybe scoring tool not yet started?"

        return current_status