import os
import shutil
import unittest
import logging
from modules.reporter import Reporter
from io import StringIO

class TestReporter(unittest.TestCase):
    log_stream = StringIO()
    logging.basicConfig(stream=log_stream, level=logging.DEBUG)

    def test_non_existing_dir(self):
        reporter = Reporter("non_existing_dir")
        score = reporter.get_score("non_existing_file")
        self.assertEqual(score, 0)

    def test_non_existing_file(self):
        existing_dir = "test_dir"
        os.makedirs(existing_dir, exist_ok=True)
        reporter = Reporter(existing_dir)
        score = reporter.get_score("non.existing.domain")
        self.assertEqual(score, 0)
        shutil.rmtree(existing_dir)

    def test_simple(self):
        existing_dir = "test_dir"
        os.makedirs(existing_dir, exist_ok=True)
        reporter = Reporter(existing_dir)
        # "time \t url \t html_lang \t detected_lang \t depth \n"
        simple_content = [
            "time\turl\tlv\tlv\t1",
            "time\turl\tlv\tlv\t1",
            "time\turl\tru\tru\t1",
        ]
        with open(os.path.join(existing_dir, 'existing_domain.tsv'), 'w', encoding="utf-8") as exf:
            exf.write('\n'.join(simple_content))
        score = reporter.get_score("existing.domain")
        self.assertEqual(score, 0.75) # (1+0.5)/2
        os.remove(os.path.join(existing_dir, 'existing_domain.tsv'))
        shutil.rmtree(existing_dir)


if __name__ == '__main__':
    unittest.main()