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
    report_config['reporter'] = {} 
    report_config['reporter']['PRIMARY_LANGUAGES'] = 'lv lt et'

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
        lang_balance = reporter.get_stats("existing.domain")['language_balance']
        self.assertEqual(lang_balance, 0.75) # (1+0.5)/2
        score = reporter.get_score("existing.domain")
        self.assertAlmostEqual(score, 0.33,  places=2) # 1 * 1/3 (primary langs balance = 1)
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
        self.assertAlmostEqual(stats['language_balance'], 0.75, places=2) # (1+0.5)/2
        self.assertAlmostEqual(stats['LDI_pages'], 0.44, places=2) # 1-(0.666*0.666+0.333*0.333) = 0.4444
        self.assertAlmostEqual(stats['LDI_words'], 0.5, places=3) # 1-(0.259 + 0.241) = 0.5
        os.remove(os.path.join(existing_dir, 'existing_domain.tsv'))
        shutil.rmtree(existing_dir)

    def test_stats_bigger(self):
        existing_dir = "test_dir"
        os.makedirs(existing_dir, exist_ok=True)
        report_config = configparser.ConfigParser()
        report_config['reporter'] = {} 
        report_config['reporter']['PRIMARY_LANGUAGES'] = 'bg cs da de el en es et fi fr ga hr hu it lt lv mt nl pl pt ro sk sl sv' # EU24
        reporter = Reporter(existing_dir, report_config)
        # "time \t url \t html_lang \t detected_lang \t depth \t num_words \n"
        simple_content = [
            "time\turl\ten\ten\t1\t294",
            "time\turl\tde\tde\t1\t627",
            "time\turl\tfr\tfr\t1\t888",
            "time\turl\tfr\tfr\t1\t888",
            "time\turl\tfr\tfr\t1\t888",
            "time\turl\tfr\tfr\t1\t888",
            "time\turl\tfr\tfr\t1\t888",
            "time\turl\tfr\tfr\t1\t888",
            "time\turl\tlv\tlv\t1\t888",
            "time\turl\tlt\tlt\t1\t888",
            "time\turl\tru\tru\t1\t888",
            "time\turl\tzh\tzh\t1\t888",
            "time\turl\tzh\tzh\t1\t888",
        ]
        with open(os.path.join(existing_dir, 'existing_domain.tsv'), 'w', encoding="utf-8") as exf:
            exf.write('\n'.join(simple_content))
        stats = reporter.get_stats("existing.domain")
        self.assertEqual(stats['lang_count'], 7) 
        self.assertAlmostEqual(stats['language_balance'], 0.31, places=2) # (1+0.16+0.16+0.16+0.16+0.16+0.333)/7
        self.assertAlmostEqual(stats['language_balance_primary'], 0.33, places=2) # (1+0.16+0.16+0.16+0.16)/5
        score = reporter.get_score("existing.domain") # 0.33333*5/24 = 0.0694
        self.assertAlmostEqual(stats['LDI_pages'], 0.73, places=2) # 1-(0.6^+0.1^+0.1^+0.1^+0.1^) = 0.4
        os.remove(os.path.join(existing_dir, 'existing_domain.tsv'))
        shutil.rmtree(existing_dir)


if __name__ == '__main__':
    unittest.main()