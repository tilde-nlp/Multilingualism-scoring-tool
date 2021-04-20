
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class ScoringSpider(CrawlSpider):
    # https://docs.scrapy.org/en/latest/topics/spiders.html
    name = "ScoringSpider"
    
    rules = (
        Rule(LinkExtractor(), callback='analyze_page', follow=True),
    )
    analyzer=None


    def analyze_page(self, response):
        # print(f"Existing settings: {self.settings.attributes.keys()}")
        # page = response.url
        # meta = response.meta
        # print("meta",meta) # meta {'rule': 0, 'link_text': '\n More Head to Head\n ', 'depth': 1, 'download_timeout': 180.0, 'download_slot': 'www.wtatennis.com', 'download_latency': 0.14538168907165527}
        # current_depths = response.meta['depth']

        self.analyzer.analyze(response)

        # And/or get more links
        # for href in response.xpath('//a/@href').getall():
        #     yield scrapy.Request(response.urljoin(href), self.parse)


