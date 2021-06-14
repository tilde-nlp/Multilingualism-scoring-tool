"""
This:
analyzes files produced by analyzer  
calculate multilinguality score 

"""
import os
import logging

def get_language_balance(langs:dict) -> float:
    lang_count = len(langs) 
    if lang_count == 0:
        return 0
    largest = max(langs, key=langs.get)
    largest_value = langs.get(largest, 1)
    if lang_count < 1 or largest_value < 1:
        return 0
    page_count = 0
    for lang, count in langs.items():
        page_count = page_count + count
    average_page_count = page_count / lang_count
    language_balance = average_page_count / largest_value
    return language_balance

class Reporter():
    roundable_stats = [ 
        'LDI_pages', 
        'LDI_words', 
        'language_balance', 
        'language_balance_primary',
        'language_balance_extended',
        'coverage_primary',
        'coverage_extended',
        ]
    def __init__(self, data_dir, report_config):
        self.logger = logging.getLogger("Reporter")
        self.data_dir = data_dir
        self.logger.log(logging.INFO, f"Reporter using data dir: {self.data_dir}")
        eu_langs = "bg cs da de el en es et fi fr ga hr hu it lt lv mt nl pl pt ro sk sl sv"
        self.primary_langs = report_config.get('reporter', 'PRIMARY_LANGUAGES', fallback=eu_langs).split(' ')
        self.extended_langs = report_config.get('reporter', 'EXTENDED_LANGUAGES', fallback='is no').split(' ')
        self.extended_langs = self.extended_langs + self.primary_langs 
        self.other_langs = report_config.get('reporter', 'OTHER_LANGUAGES', fallback='').split(' ')
        self.logger.log(logging.INFO, f"Reporter using PRIMARY_LANGUAGES: {self.primary_langs}")
        self.logger.log(logging.INFO, f"Reporter using EXTENDED_LANGUAGES: {self.extended_langs}")
        self.logger.log(logging.INFO, f"Reporter using OTHER_LANGUAGES: {self.other_langs}")

    def get_stats(self, domain):
        langs = {}
        langs_words = {}
        stats = {
            'LDI_pages':0,
            'LDI_words':0,
            'language_balance':0,
            'language_balance_primary':0,
            'language_balance_extended':0,
            'lang_count':0,
            'langs':langs,
            'langs_words':langs_words,
            'total_pages':0,
            'total_words':0,
            'wo_lang_pages':0,
            'wo_lang_words':0,
            'coverage_primary':0,
            'covered_primary':"0",
            'coverage_extended':0,
            'covered_extended':"0",
        }
        if not os.path.exists(self.data_dir):
            self.logger.error(f"Could not find data dir: {self.data_dir}")
            return stats
        filename = domain.replace(".","_")
        filename = os.path.join(self.data_dir, filename + ".tsv")
        if not os.path.exists(filename):
            self.logger.debug(f"Could not find file for score calculation: {filename}")
            return stats
        rows = []

        with open(filename, 'r', encoding='utf-8') as inf:
            for row in inf:
                data = row.split('\t')
                try:
                    assert(len(data) == 6)
                except AssertionError:
                    self.logger.log(logging.ERROR,f"Length of data is not 6 tab separeted elems; data was '{row}'")
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
        lang_count = len(langs)

        stats['lang_count'] = lang_count if lang_count > 0 else 1

        # language_balance = average(count_l1, count_l2, ..., count_ln)/count_max
        try:
            largest = max(langs, key=langs.get)
        except:
            # if no largest, there are no text/languages detected
            self.logger.error(f"Could not detect 'largest' language for domain: {domain}")
            return stats
        largest_value = langs.get(largest, 1)
        langs_primary = {}
        langs_extended = {}
        for lang, count in langs.items():
            if lang in self.primary_langs:
                langs_primary[lang] = count
            if lang in self.extended_langs:
                langs_extended[lang] = count
        coverage_primary = 0 # How many of EU languages (or some other set) are present in a website 0(min)-1(max)
        coverage_extended = 0
        total_words = 0
        page_count = 0
        lang_stats_for_debug = ""
        for lang, count in langs.items():
            page_count = page_count + count
            total_words = total_words + langs_words.get(lang, 0)
            lang_stats_for_debug = lang_stats_for_debug + "{}:{}:{} ".format(lang, count, langs_words.get(lang, 0))
            if lang in self.primary_langs:
                coverage_primary = coverage_primary + 1
            if lang in self.extended_langs:
                coverage_extended = coverage_extended + 1
        count_primary_langs = len(self.primary_langs) if len(self.primary_langs) > 0 else 1 # avoid /0 
        count_extended_langs = len(self.extended_langs) if len(self.extended_langs) > 0 else 1
        stats['covered_primary'] = f"{coverage_primary}"
        stats['coverage_primary'] = coverage_primary/count_primary_langs
        stats['covered_extended'] = f"{coverage_extended}"
        stats['coverage_extended'] = coverage_extended/count_extended_langs

        stats['language_balance'] = get_language_balance(langs)
        stats['language_balance_primary'] = get_language_balance(langs_primary)
        stats['language_balance_extended'] = get_language_balance(langs_extended)


        # Lieberson’s diversity index (LDI) (Lieberson 1981)
        # LDI = 1 - ΣPi*Pi , where Pi represents the share of i-th language speakers in a community
        sum_pi_squared = 0
        page_count = 1 if page_count == 0 else page_count # avoid /0
        for lang, count in langs.items():
            share = count/page_count
            sum_pi_squared = sum_pi_squared + (share * share)
        stats['LDI_pages'] = 1 - sum_pi_squared
        stats['LDI_pages'] = stats['LDI_pages']
        # LDI calculated using words, not page counts
        sum_pi_squared_words = 0
        total_words = 1 if total_words == 0 else total_words # avoid /0
        for lang, count in langs_words.items():
            share = count/total_words
            sum_pi_squared_words = sum_pi_squared_words + (share * share)
        stats['LDI_words'] = 1 - sum_pi_squared_words
        stats['LDI_words'] = stats['LDI_words']

        self.logger.log(logging.DEBUG,f"Domain {domain}, language count {stats['lang_count']}, language_balance {stats['language_balance']},language_balance_primary {stats['language_balance_primary']},  largest {largest}:{largest_value}, all-{lang_stats_for_debug}, pages with N/A lang:{stats['wo_lang_pages']}, total_pages:{stats['total_pages']}, LDI_pages {stats['LDI_pages']}, LDI_words {stats['LDI_words']}")

        return stats


    def get_score_from_stats(self, stats):
        if stats == None:
            return 0
        self.logger.log(logging.DEBUG, f"Reporter using PRIMARY_LANGUAGES: {self.primary_langs}")
        score = stats['language_balance_primary'] * stats['coverage_primary']
        return score


    def get_score(self, domain):
        score = 0
        stats = self.get_stats(domain)
        return self.get_score_from_stats(stats)

