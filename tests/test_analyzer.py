import os
import unittest
import logging
from io import StringIO
from scrapy.http.request import Request
# from scrapy.http.response import Response
from scrapy.http.response.text import TextResponse

from modules.analyzer import Analyzer
from modules.common_functions import extractDomain
import time

class TestAnalyzer(unittest.TestCase):
    log_stream = StringIO()
    logging.basicConfig(stream=log_stream, level=logging.DEBUG)
    
    def test_simple(self):
        test_dir = "test_dir"
        analyzer = Analyzer(test_dir)
        body = '<!DOCTYPE html><html lang="lv"><head><title>Teksts latviešu valodā.</title></head><body><h1>Testa lapa teksta izvilkšanas un valodas noteikšanas pārbaudei.</h1><p>Daudz vairāk teksta latviešu valodā. Teksts ir mutvārdos izteikts vai rakstveidā fiksēts loģiski strukturēts, funkcionāli vienots jēdzieniski saistītu izteikumu kopums vai atsevišķs izteikums. Literatūrā teksts ir jebkurš objekts, ko var "lasīt", vai šis objekts ir literārais darbs, ielas apzīmējums, ēku izvietojums pilsētas blokā vai apģērbu stils. Tas ir saskaņots zīmju kopums, kas pārraida kādu informatīvu vēstījumu. Šis simbolu komplekts tiek uzskatīts par informatīvā ziņojuma saturu, nevis tā fizisko formu vai veidu, kurā tas ir attēlots.</p><p>Vēl vairāk teksta latviešu valodā.</p></body></html>'
        body = body.encode('utf-8')
        url = 'http://dummy.url/'
        test_request = Request(url)
        test_response = TextResponse(url, status=200, body=body, request=test_request)
        test_response.meta['depth'] = 1

        analyzer.analyze(test_response)
        
        domain = extractDomain(url)
        filename = domain.replace(".","_")
        test_file = os.path.join(test_dir, filename + '.tsv')
        
        self.assertTrue(os.path.exists(test_file))
        with open(test_file, 'r', encoding="utf-8") as outf:
            content = outf.read()
            data = content.split('\t')
            self.assertNotEqual(data[2],'ru') # lv
            self.assertEqual(data[3],'lv')

if __name__ == '__main__':
    unittest.main()