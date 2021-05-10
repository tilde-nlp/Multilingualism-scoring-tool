"""
This:
analyzes files produced by analyzer  
calculate multilinguality score 

"""
import os
import logging

class Reporter():
    def __init__(self, data_dir):
        self.logger = logging.getLogger("Reporter")
        self.data_dir = data_dir
        self.logger.debug(f"Reporter using data dir: {self.data_dir}")


    def get_stats(self, domain):
        langs = {}
        langs_words = {}
        stats = {
            'language_balance':0,
            'lang_count':0,
            'langs':langs,
            'langs_words':langs_words,
            'total_pages':0,
            'total_words':0,
            'wo_lang_pages':0,
            'wo_lang_words':0,
        }
        if not os.path.exists(self.data_dir):
            self.logger.log(logging.ERROR,f"Could not find data dir: {self.data_dir}")
            return stats
        filename = domain.replace(".","_")
        filename = os.path.join(self.data_dir, filename + ".tsv")
        if not os.path.exists(filename):
            self.logger.log(logging.ERROR,f"Could not find file for score calculation: {filename}")
            return stats
        rows = []

        with open(filename, 'r', encoding='utf-8') as inf:
            for row in inf:
                data = row.split('\t')
                try:
                    assert(len(data) == 6)
                except AssertionError:
                    self.logger.log(logging.ERROR,f"Length of data is not 5 tab separeted elems; data was '{row}'")
                    continue
                words_in_a_doc = int(data[5])
                if data[3] == "None": # Dont consider "None" as language
                    stats['wo_lang_pages'] = stats['wo_lang_pages'] + 1
                    stats['wo_lang_words'] = stats['wo_lang_words'] + words_in_a_doc
                else:
                    langs[data[3]] = langs.get(data[3], 0) + 1
                    langs_words[data[3]] = langs_words.get(data[3], 0) + words_in_a_doc
                stats['total_pages'] = stats['total_pages'] + 1
                stats['total_words'] = stats['total_words'] + words_in_a_doc
        # print(langs)
        lang_count = len(langs)

        stats['lang_count'] = lang_count if lang_count > 0 else 1

        # update: ELRC. Multilingualism Scoring Tool. Language Balance.xlsx
        # language_balance = average(count_l1, count_l2, ..., count_ln)/count_max
        largest = max(langs, key=langs.get)
        largest_value = langs.get(largest, 1)
        page_count = 0
        lang_stats_for_debug = ""
        for lang, count in langs.items():
            page_count = page_count + count
            lang_stats_for_debug = lang_stats_for_debug + "{}:{}:{} ".format(lang, count, langs_words.get(lang, 0))
        average_page_count = page_count / stats['lang_count']
        stats['language_balance'] = average_page_count / largest_value
    
        self.logger.log(logging.INFO,f"Domain {domain}, language count {stats['lang_count']}, language_balance {stats['language_balance']},  largest {largest}:{largest_value}, all-{lang_stats_for_debug}, pages with N/A lang:{stats['wo_lang_pages']}, total_pages:{stats['total_pages']}")

        return stats


    def get_score_from_stats(self, stats):
        if stats == None:
            return 0
        factor = 1 #if stats['lang_count'] > 1 else 0 # lang_count/26    # If single lang balance == 0 
        score = factor * stats['language_balance']
        return score


    def get_score(self, domain):
        score = 0
        stats = self.get_stats(domain)
        return self.get_score_from_stats(stats)

