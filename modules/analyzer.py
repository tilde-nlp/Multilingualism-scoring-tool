"""
We have not yet decided on analysis process.

Idea is to parse response and write findings to file, which has domain as filename
Format would be tsv
"""
import os
from urllib.parse import urlparse
import datetime
import logging
from modules.common_functions import extractDomain, extractText
from modules.lang_detector import LanguageDetector
from scrapy.exceptions import NotSupported

class Analyzer():
    def __init__(self, data_dir):
        self.logger = logging.getLogger("Analyzer")
        self.data_dir = data_dir
        self.language_detector = LanguageDetector()
        os.makedirs(self.data_dir, exist_ok=True)
        self.logger.debug(f"Data dir: {self.data_dir}")       


    def analyze(self, response):
        # response is https://docs.scrapy.org/en/latest/topics/request-response.html#scrapy.http.Response
        url = response.url
        # meta = response.meta
        # print("meta",meta) # meta {'rule': 0, 'link_text': '\n More Head to Head\n ', 'depth': 1, 'download_timeout': 180.0, 'download_slot': 'www.wtatennis.com', 'download_latency': 0.14538168907165527}
        current_depth = response.meta['depth']

        time_now = datetime.datetime.now().strftime("%H:%M:%S")

        try:
            html_language = response.xpath('//html/@lang').get()
        except NotSupported as e:
            self.logger.debug(f"Exception while extracting declared html language: {e}")
            # "Response content isn't text"
            # @TODO Analyze other kinds of responses (PDF, ...) too
            return
        plaintext = extractText(response)
        detected_main_language = self.language_detector.predict_lang(plaintext)
        if detected_main_language == None:
            detected_main_language = "None"

        domain = extractDomain(url)
        filename = domain.replace(".","_")

        total_words = len(plaintext.split())

        outfilename = os.path.join(self.data_dir, filename + ".txt")
        with open(outfilename, 'a', encoding="utf-8") as outf:
            outf.write('\n\n==========================================\n')
            outf.write(f"Detected language: {detected_main_language}\n")
            outf.write(f"URL: {url}\n")
            outf.write(plaintext)

        outfilename = os.path.join(self.data_dir, filename + ".tsv")
        with open(outfilename, 'a', encoding="utf-8") as outf:
            outf.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(time_now, url, html_language, detected_main_language, current_depth, total_words))
