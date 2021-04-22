import os
import shutil
import sys
import threading

# import tornado.ioloop
# import tornado.web

from urllib.parse import urlparse
import configparser
# pip install scrapy # Use version 2.4.0 # https://github.com/scrapy/scrapy/blob/master/LICENSE
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from modules.scoring_tool import ScoringTool


def run_scoring(urls=None):
    if urls == None:
        urls = [
            # 'https://www.bmw.com/',  # quite mulitlingual
            # 'https://www.memorywater.com/', # 19 links l2, 3 langs 
            # 'https://www.tilde.lv/',    # mulitlingual .ee .lt
            'http://gorny.edu.pl/', # 5 links l2, mono
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

    scorer = ScoringTool()
    
    score = scorer.initialize(urls)

    print("Done crawling ")
    return score    # returns last score for testing


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='This is tool for evaluation of website multilinguality!')
    parser.add_argument('-u', '--urls', nargs='+', help='Starting urls to evaluate, domains will be extracted from them.')
    args = parser.parse_args()
    urls = args.urls
    run_scoring(urls)
