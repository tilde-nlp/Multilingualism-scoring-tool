import os
import shutil
import sys
import threading

from urllib.parse import urlparse
import configparser
# pip install scrapy # Use version 2.4.0 # https://github.com/scrapy/scrapy/blob/master/LICENSE
import scrapy
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from modules.spider import ScoringSpider
from modules.spider import ScoringSpiderSitemap
from modules.analyzer import Analyzer
from modules.reporter import Reporter
from modules.common_functions import extractDomain

from twisted.internet import reactor, defer

from scrapy.utils.project import get_project_settings

class ScoringTool():

    def get_crawl_progress_status(self):
        current_status = {}
        if self.status is None:
            current_status["status"] = "error" 
            current_status["message"] = "No stats - nothing to analyze. Maybe scoring tool not yet initialized?"
            return current_status
        current_status["status"] = self.status
        current_status["message"] = self.status
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
            stats = self.reporter.get_stats(domain)
            # stats: 'language_balance', 'lang_count', 'langs', # For full list see Reporter
            score = self.reporter.get_score_from_stats(stats)
            print("Domain: {}, score: {:0.3f}, langs: {}".format(domain, score, stats['langs']))
            current_status[domain] = (score, stats)
        # return (score, stats)
        return current_status
    
    def do_crawling_in_separate_thread(self):
        # https://stackoverflow.com/questions/14274916/execute-twisted-reactor-run-in-a-thread/14282640
        # process = CrawlerProcess(settings=settings)
        process = CrawlerRunner(settings=self.settings)
        

        spider = ScoringSpider  # CrawlerProcess accepts Spider class or Crawler instances
        sitemapspider = ScoringSpiderSitemap

        spider.start_urls = self.urls
        spider.allowed_domains = self.allowed_domains 
        spider.analyzer = Analyzer(self.analyzer_data_dir)
        sitemapspider.allowed_domains = self.allowed_domains
        sitemapspider.sitemap_urls = self.sitemap_urls
        sitemapspider.analyzer = spider.analyzer

        # process.crawl(sitemapspider)
        # process.crawl(spider)
        @defer.inlineCallbacks
        def crawl():
            yield process.crawl(sitemapspider)
            yield process.crawl(spider)
            print("Crawling in twisted done") # Actual crawl done
            self.status = "crawling finished"
            # reactor.stop()

        crawl()

        # reactor.run()
        threading.Thread(target=reactor.run, args=(False,)).start()
        self.status = "crawling"

        current_status = {}
        current_status["status"] = self.status 
        current_status["message"] = f"Started crawling of {len(spider.start_urls)} urls."
        return current_status



    def initialize(self, urls):
        self.urls = urls
        
        self.sitemap_urls = []
        for url in urls:
            parsed_url = urlparse(url)
            self.sitemap_urls.append(f'{parsed_url.scheme}://{parsed_url.netloc}/sitemap.xml')
            self.sitemap_urls.append(f'{parsed_url.scheme}://{parsed_url.netloc}/robots.txt')

        # settings = {}
        self.settings = get_project_settings()

        config = configparser.ConfigParser()
        config.read('settings.ini')
        def override_default_crawler_config():
            for key in config['crawler']:
                self.settings[key.upper()] = config.get('crawler', key, fallback='')
        override_default_crawler_config()

        self.analyzer_data_dir = config.get('analyzer', 'data_dir', fallback='')
        self.reporter = Reporter(self.analyzer_data_dir)
        self.allowed_domains = [extractDomain(i) for i in urls]
        # print(f'\nPrepared allowed_domains {allowed_domains}\n')

        def dump_config_to_file_for_debug():
            with open('settings.cfg', 'w', encoding='utf-8') as of:
                for key, value in self.settings.items():
                    of.write(f'{key}, {value}\n')
        dump_config_to_file_for_debug()

        def clear_log_file(): # Use new log file for each run
            try:
                os.remove(self.settings['LOG_FILE'])
            except PermissionError:
                pass
            except FileNotFoundError:
                pass
        clear_log_file()

        def clean_analyzed_dir_before_running():
            try:
                shutil.rmtree(self.analyzer_data_dir)
            except Exception as e:
                print("Exception "+str(e))
                pass
        clean_analyzed_dir_before_running()

        if self.status is None:
            self.status = "initialized"