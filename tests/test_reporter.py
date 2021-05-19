import os
import shutil
import unittest
import logging
from modules.reporter import Reporter
from io import StringIO
import configparser

class TestReporter(unittest.TestCase):
    log_stream = StringIO()
    logging.basicConfig(stream=log_stream, level=logging.DEBUG)
    report_config = configparser.ConfigParser()
    report_config['Reporter'] = {} 
    report_config['Reporter']['PRIMARY_LANGUAGES'] = 'lv lt et'

    def test_non_existing_dir(self):
        reporter = Reporter("non_existing_dir", TestReporter.report_config)
        score = reporter.get_score("non_existing_file")
        self.assertEqual(score, 0)

    def test_non_existing_file(self):
        existing_dir = "test_dir"
        os.makedirs(existing_dir, exist_ok=True)
        reporter = Reporter(existing_dir, TestReporter.report_config)
        score = reporter.get_score("non.existing.domain")
        self.assertEqual(score, 0)
        shutil.rmtree(existing_dir)

    def test_simple(self):
        existing_dir = "test_dir"
        os.makedirs(existing_dir, exist_ok=True)
        reporter = Reporter(existing_dir, TestReporter.report_config)
        # "time \t url \t html_lang \t detected_lang \t depth \t num_words \n"
        simple_content = [
            "time\turl\tlv\tlv\t1\t294",
            "time\turl\tlv\tlv\t1\t627",
            "time\turl\tru\tru\t1\t888",
        ]
        with open(os.path.join(existing_dir, 'existing_domain.tsv'), 'w', encoding="utf-8") as exf:
            exf.write('\n'.join(simple_content))
        score = reporter.get_score("existing.domain")
        self.assertEqual(score, 0.75) # (1+0.5)/2
        os.remove(os.path.join(existing_dir, 'existing_domain.tsv'))
        shutil.rmtree(existing_dir)

    def test_stats(self):
        existing_dir = "test_dir"
        os.makedirs(existing_dir, exist_ok=True)
        reporter = Reporter(existing_dir, TestReporter.report_config)
        # "time \t url \t html_lang \t detected_lang \t depth \t num_words \n"
        simple_content = [
            "time\turl\tlv\tlv\t1\t294",
            "time\turl\tlv\tlv\t1\t627",
            "time\turl\tru\tru\t1\t888",
        ]
        with open(os.path.join(existing_dir, 'existing_domain.tsv'), 'w', encoding="utf-8") as exf:
            exf.write('\n'.join(simple_content))
        stats = reporter.get_stats("existing.domain")
        self.assertEqual(stats['lang_count'], 2) 
        self.assertAlmostEqual(stats['language_balance'], 0.75, places=3) # (1+0.5)/2
        self.assertAlmostEqual(stats['LDI_pages'], 0.4444, places=3) # 1-(0.666*0.666+0.333*0.333) = 0.4444
        self.assertAlmostEqual(stats['LDI_words'], 0.5, places=3) # 1-(0.259 + 0.241) = 0.5
        os.remove(os.path.join(existing_dir, 'existing_domain.tsv'))
        shutil.rmtree(existing_dir)


if __name__ == '__main__':
    unittest.main()