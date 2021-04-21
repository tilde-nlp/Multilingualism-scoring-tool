import os
import shutil
import sys
from urllib.parse import urlparse
import configparser
# pip install scrapy # Use version 2.4.0 # https://github.com/scrapy/scrapy/blob/master/LICENSE
import scrapy
from scrapy.crawler import CrawlerProcess
from modules.spider import ScoringSpider
from modules.analyzer import Analyzer
from modules.reporter import Reporter
from modules.common_functions import extractDomain

from scrapy.utils.project import get_project_settings

def run_scoring(urls=None):
    if urls == None:
        urls = [
            # 'https://www.bmw.com/',  # quite mulitlingual
            'https://www.memorywater.com/', # 19 links l2, 3 langs 
            # 'https://www.tilde.lv/',    # mulitlingual .ee .lt
            # 'http://gorny.edu.pl/', # 5 links l2, mono
            # 'https://www.norden.org/',
            # 'https://europa.eu/',
            # 'https://globalvoices.org/',
            # 'https://www.royalfloraholland.com',
            # 'https://luxexpress.com',
            # 'https://aerodium.technology',
            # 'https://www.madaracosmetics.com',
            # 'https://www.airbaltic.com',
            # 'https://census.gov.uk/help/languages-and-accessibility/languages',

        ]
    sitemap_urls = []
    for url in urls:
        parsed_url = urlparse(url)
        sitemap_urls.append(f'{parsed_url.scheme}://{parsed_url.netloc}/sitemap.xml')

    allowed_domains = [extractDomain(i) for i in urls]
    # print(f'\nPrepared allowed_domains {allowed_domains}\n')

    # settings = {}
    settings = get_project_settings()

    config = configparser.ConfigParser()
    config.read('settings.ini')
    def override_default_crawler_config():
        for key in config['crawler']:
            settings[key.upper()] = config.get('crawler', key, fallback='')
    override_default_crawler_config()

    # Dump config to file for debug
    with open('settings.cfg', 'w', encoding='utf-8') as of:
        for key, value in settings.items():
            of.write(f'{key}, {value}\n')

    # Use new log file for each run
    try:
        os.remove(settings['LOG_FILE'])
    except PermissionError:
        pass
    except FileNotFoundError:
        pass

    analyzer_data_dir = config.get('analyzer', 'data_dir', fallback='')
    # Clean analyzed_dir before running
    try:
        shutil.rmtree(analyzer_data_dir)
    except Exception as e:
        print("Exception "+str(e))
        pass

    process = CrawlerProcess(settings=settings)

    spider = ScoringSpider  # CrawlerProcess accepts Spider class or Crawler instances
    spider.start_urls = urls
    spider.sitemap_urls = sitemap_urls
    spider.allowed_domains = allowed_domains 
    spider.analyzer = Analyzer(analyzer_data_dir)

    process.crawl(spider)
    process.start()
    # process.stop()

    reporter = Reporter(analyzer_data_dir)
    for domain in allowed_domains:
        stats = reporter.get_stats(domain)
        # stats: 'language_balance', 'lang_count', 'langs', # For full list see Reporter
        score = reporter.get_score_from_stats(stats)
        print("Domain: {}, score: {:0.3f}, langs: {}".format(domain, score, stats['langs']))


    print("Done crawling ")
    return score    # returns last score for testing


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='This is tool for evaluation of website multilinguality!')
    parser.add_argument('-u', '--urls', nargs='+', help='Starting urls to evaluate, domains will be extracted from them.')
    args = parser.parse_args()
    urls = args.urls
    run_scoring(urls)
