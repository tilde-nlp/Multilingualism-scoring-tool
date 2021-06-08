import os
import shutil
import sys
# import threading
import logging
import time
from datetime import datetime
import json
from collections import OrderedDict

from urllib.parse import urlparse
# pip install scrapy # Use version 2.4.0 # https://github.com/scrapy/scrapy/blob/master/LICENSE
import scrapy
from scrapy import signals
from scrapy.crawler import CrawlerProcess, CrawlerRunner, Crawler
from modules.spider import ScoringSpider
from modules.spider import ScoringSpiderSitemap
from modules.analyzer import Analyzer
from modules.reporter import Reporter
from modules.common_functions import extractDomain, is_ok_job_name

from twisted.internet import reactor, defer

from scrapy.utils.project import get_project_settings

import multiprocessing
from multiprocessing import Process, Queue


class ScoringTool():
    def __init__(self, config, report_config):
        self.logger = logging.getLogger("ScoringTool")
        
        # settings = {}
        self.settings = get_project_settings()        

        self.config = config
        def override_default_crawler_config():
            for key in self.config['crawler']:
                self.settings[key.upper()] = self.config.get('crawler', key, fallback='')
        override_default_crawler_config()

        self.analyzer_data_dir = self.config.get('analyzer', 'data_dir', fallback='')
        self.jobtitle = self.config.get('analyzer', 'default_job_title', fallback='')
        self.reporter = Reporter(self.analyzer_data_dir, report_config)
        self.p = None
        self.process = None
        self.queue = Queue()

        self.status = "ready" # ready, crawling, stopping, error 


    def stop_crawler(self, spider):
        for crawler in self.process.crawlers:
            if crawler.spider == spider:
                crawler.stop()        
        if len(self.process.crawlers) <= 1:
            current = multiprocessing.current_process()
            if current.name.startswith("Process"):
                self.queue.put("Finished Crawling")


    def get_crawl_progress_status(self) -> dict:
        try:
            if self.queue.get_nowait() == "Finished Crawling":
                self.process.stop()
                self.status = "stopping"
        except Exception as e:
            print(e)
            pass
        try:
            if self.process is None:
                self.status = "ready"
            elif len(self.process.crawlers) > 0 and self.status=="stopping":
                self.status = "stopping"
            elif len(self.process.crawlers) > 0:
                self.status = "crawling"
            elif self.p.is_alive():
                self.status = "stopping"
            else:
                self.status = "ready"
        except Exception as e:
            print(f"Exception: {e}")

        current_status = {}
        try:
            current_status["status"] = self.status
            current_status["message"] = self.status
        except AttributeError:
            current_status["status"] = "error" 
            current_status["message"] = "No stats - nothing to analyze. Maybe scoring tool not yet initialized?"
        return current_status


    def get_current_stats(self) -> dict:
        current_status = {}
        try: 
            allowed_domains = self.allowed_domains
        except AttributeError:
            current_status["status"] = "error" 
            current_status["message"] = "No stats - nothing to analyze. Maybe scoring tool not yet initialized?"
            return current_status

        job_score = 0
        nonzero_domains = 0 # Domains with score 0 excluded

        for domain in self.allowed_domains:
            try:
                stats = self.reporter.get_stats(domain)
            except Exception as e:
                self.logger.error(f"Domain {domain}, could not create stats: {e}")
                continue
            # stats: 'language_balance', 'lang_count', 'langs', # For full list see Reporter
            score = self.reporter.get_score_from_stats(stats)
            score = score * 100
            if score > 0:
                job_score = job_score + score
                nonzero_domains = nonzero_domains + 1
            score = "{:0.2f}".format(score)
            for key, value in stats.items(): 
                if key in Reporter.roundable_stats: # Convert to 0-100%
                    value = value * 100
                    stats[key] = "{:0.2f}".format(value)
            current_status[domain] = (score, stats)
        if nonzero_domains > 0:
            job_score = job_score / nonzero_domains
        job_score = "{:0.2f}".format(job_score)
        # current_status["job_score"] = job_score
        return current_status
       

    def get_current_stats_for_display(self, stats_to_display:list) -> dict:
        current_stats = self.get_current_stats()
        pretty_stats = OrderedDict()
        for domain, (score, stats) in current_stats.items():
            display_stats = OrderedDict()
            for key in stats_to_display:
                display_stats[key] = stats.get(key)
            pretty_stats[domain] = (score, display_stats)
        return pretty_stats


    def save_results_as_json(self) -> str:
        current_stats = self.get_current_stats()
        saved_results_dir = self.config.get('app', 'saved_results_dir', fallback='saved_results') 
        os.makedirs(saved_results_dir, exist_ok=True)
        current_date = datetime.today().strftime('%Y%m%d')
        local_filename = os.path.join(saved_results_dir, f'{self.jobtitle}_{current_date}.json')
        with open(local_filename, 'w', encoding='utf-8') as saved_res_f:
            json.dump(current_stats, saved_res_f)
        return local_filename


    def save_results_as_full_csv(self) -> str:
        current_stats = self.get_current_stats()
        saved_results_dir = self.config.get('app', 'saved_results_dir', fallback='saved_results') 
        os.makedirs(saved_results_dir, exist_ok=True)
        current_date = datetime.today().strftime('%Y%m%d')
        local_filename = os.path.join(saved_results_dir, f'{self.jobtitle}_{current_date}_all.csv')
        with open(local_filename, 'w', encoding='utf-8') as saved_res_f:
            # write header
            (first_score, first_stats) = next(iter(current_stats.values()))
            saved_res_f.write(f"domain,score,{','.join(first_stats.keys())}\n")
            # write all domains
            for domain, (score, stats) in current_stats.items():
                items = [domain, score]
                for key, value in stats.items():
                    items.append(value)
                items = [str(item).replace(',',';').replace('{','').replace('}','') for item in items]
                csv_row = ",".join(items)
                saved_res_f.write(f"{csv_row}\n")
        return local_filename


    def save_results_as_csv(self, stats_to_display:list) -> str:
        saved_results_dir = self.config.get('app', 'saved_results_dir', fallback='saved_results') 
        os.makedirs(saved_results_dir, exist_ok=True)
        current_date = datetime.today().strftime('%Y%m%d')
        local_filename = os.path.join(saved_results_dir, f'{self.jobtitle}_{current_date}.csv')
        current_stats = self.get_current_stats_for_display(stats_to_display)
        with open(local_filename, 'w', encoding='utf-8') as saved_res_f:
            saved_res_f.write(f"domain,score,{','.join(stats_to_display)}\n")
            for domain, (score, stats) in current_stats.items():
                items = [domain, score]
                for key, value in stats.items():
                    items.append(value) 
                csv_row = ",".join(items)
                saved_res_f.write(f"{csv_row}\n")
        return local_filename


    def start_crawl(self, urls: list, hops:int, jobtitle:str="") -> dict:
        if self.status in ["crawling", "stopping"]:
            current_status = {}
            current_status["status"] = "error" 
            current_status["message"] = "Can not start, already crawling."
            return current_status
        if jobtitle and not is_ok_job_name(jobtitle):
            response = {}
            response["status"] = "error" 
            response["message"] = "Only letters and numbers allowed in job title."
            self.logger.debug(f"title was not alphanumeric: {jobtitle}")
            return response
        if jobtitle:
            self.jobtitle = jobtitle
        def verify_and_try_to_fix_urls(urls: list) -> list:
            stripped_urls = [url.strip() for url in urls if url.strip()]
            fixed_urls = []
            for url in stripped_urls:
                if not url.startswith('http'): # prepend protocol if not present
                    url = 'http://' + url
                fixed_urls.append(url)
            return fixed_urls
        self.urls = verify_and_try_to_fix_urls(urls)

        self.sitemap_urls = []
        for url in self.urls:
            parsed_url = urlparse(url)
            self.sitemap_urls.append(f'{parsed_url.scheme}://{parsed_url.netloc}/sitemap.xml')
            self.sitemap_urls.append(f'{parsed_url.scheme}://{parsed_url.netloc}/robots.txt')


        # override DEPTH_LIMIT with "hops" from UI
        self.settings['DEPTH_LIMIT'] = hops

        self.allowed_domains = [extractDomain(i) for i in self.urls]
        self.allowed_domains = list(set(self.allowed_domains))
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
        spider.start_urls = self.urls
        spider.allowed_domains = self.allowed_domains 
        spider.analyzer = Analyzer(self.analyzer_data_dir)
        # sitemapspider = ScoringSpiderSitemap
        # sitemapspider.allowed_domains = self.allowed_domains
        # sitemapspider.sitemap_urls = self.sitemap_urls
        # sitemapspider.analyzer = spider.analyzer    # the same as spider

        self.process = CrawlerProcess(settings=self.settings)
        # self.process.crawl(sitemapspider)
        self.process.crawl(spider)

        for crawler in self.process.crawlers:
            crawler.signals.connect(self.stop_crawler, signal=signals.spider_closed)

        # Similar approach:
        # https://stackoverflow.com/questions/11528739/running-scrapy-spiders-in-a-celery-task
        # Alternative # https://stackoverflow.com/questions/14274916/execute-twisted-reactor-run-in-a-thread/14282640
        # threading VERY slow in Docker
        # threading.Thread(target=self.process.start, args=(False,)).start()
        self.p = Process(target=self.process.start, args=(self.queue,))
        self.p.start()

        
        self.status = "crawling"
        current_status = {}
        current_status["status"] = self.status 
        current_status["message"] = f"Started crawling of {len(spider.start_urls)} urls."
        return current_status


    def stop_crawl(self) -> dict:
        if self.status == "crawling":
            try:
                self.process.stop()
                time.sleep(0.1)
                self.p.terminate()
                time.sleep(0.1)
            except Exception as e:
                print(e)
            self.status = "stopping"
        elif self.status == "stopping":
            self.p.terminate()
            time.sleep(0.1)
            if not self.p.is_alive():
                self.p.join(timeout=1.0)
                self.status = "ready"

        current_status = {}
        try:
            current_status["status"] = self.status
            current_status["message"] = self.status
        except AttributeError:
            current_status["status"] = "error" 
            current_status["message"] = "No stats - nothing to analyze. Maybe scoring tool not yet started?"

        return current_status