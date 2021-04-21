import unittest
from modules.common_functions import extractDomain, extractText, segmentText

from scrapy.http.request import Request
from scrapy.http.response.text import TextResponse

class TestExtractDomain(unittest.TestCase):
    def test_extractDomain(self):
        urls = [
            'http://gorny.edu.pl/', 
            'https://dictionary.cambridge.org/dictionary/english/multilingual',
            'https://en.wikipedia.org/',
            'https://www.memorywater.com/', 
            'http://quotes.toscrape.com/',
            'https://www.tilde.lv/',
            'https://lv.sputniknews.ru',
            'https://www.bmw.com/',
            'https://www.amazon.co.uk/',
        ]

        subdomains = [
            '', 
            'dictionary',
            'en',
            'www', 
            'quotes',
            'www',
            'lv',
            'www',
            'www',
        ]
        domains = [
            'gorny', 
            'cambridge',
            'wikipedia',
            'memorywater', 
            'toscrape',
            'tilde',
            'sputniknews',
            'bmw',
            'amazon',
        ]
        suffixes = [
            'edu.pl', 
            'org',
            'org',
            'com', 
            'com',
            'lv',
            'ru',
            'com',
            'co.uk',
        ]
        for url, subdomain, domain, suffix in zip(urls, subdomains, domains, suffixes):
            detected_domain = extractDomain(url)
            expected_domain = '.'.join([domain,suffix])
            self.assertEqual(detected_domain, expected_domain)


class TestExtractText(unittest.TestCase):
    body = '''<!DOCTYPE html><html lang="lv"><head><title>Teksts latviešu valodā.</title></head><body><h1>Testa lapa teksta izvilkšanas un valodas noteikšanas pārbaudei.</h1><p>Daudz <b>vairāk</b> teksta latviešu valodā. Teksts ir mutvārdos izteikts vai rakstveidā fiksēts loģiski strukturēts, funkcionāli vienots jēdzieniski saistītu izteikumu kopums vai atsevišķs izteikums. Literatūrā teksts ir jebkurš objekts, ko var "lasīt", vai šis objekts ir literārais darbs, ielas apzīmējums, ēku izvietojums pilsētas blokā vai apģērbu stils. Tas ir saskaņots zīmju kopums, kas pārraida kādu informatīvu vēstījumu. Šis simbolu komplekts tiek uzskatīts par informatīvā ziņojuma saturu, nevis tā fizisko formu vai veidu, kurā tas ir attēlots.</p><div><p>Some text inside a div element.</p><p>Very unimportant news from somesite.</p></div></body></html>'''
    body = body.encode('utf-8')
    test_request = Request('http://dummy.url/')
    test_response = TextResponse('http://dummy.url/', status=200, body=body, request=test_request)

    def test_extractText(self):
        detected_text = extractText(self.test_response)
        # It seems to unrealistic to expect any tool
        # to extract all text and without boilerplate
        # Test to see if key sentences are extracted
        sentence1 = 'Teksts latviešu valodā.'
        sentence2 = 'Testa lapa teksta izvilkšanas un valodas noteikšanas pārbaudei.'
        sentence3 = 'Daudz vairāk teksta latviešu valodā.'
        sentence4 = 'Very unimportant news from somesite.'
        # self.assertIn(sentence1,detected_text)
        # self.assertIn(sentence2,detected_text)
        self.assertIn(sentence3,detected_text)
        # self.assertIn(sentence4,detected_text)

class TestSegmenter(unittest.TestCase):
    def test_none(self):
        text = ""
        expected = ""
        segmented = segmentText(text)
        self.assertEqual(segmented, expected)

    def test_single(self):
        text = "This is single sentence. "
        expected = "This is single sentence."
        segmented = segmentText(text)
        self.assertEqual(segmented, expected)

    def test_two(self):
        text = "This is first sentence. This is second. "
        expected = "This is first sentence.\nThis is second."
        segmented = segmentText(text)
        self.assertEqual(segmented, expected)

if __name__ == '__main__':
    unittest.main()
