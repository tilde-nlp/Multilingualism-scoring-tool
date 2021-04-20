import logging

# import fasttext
# # pip install pybind11 # if required
# # pip install fasttext
# # https://github.com/facebookresearch/fastText/issues/1067
# fasttext.FastText.eprint = lambda x: None # to remove load warning

import langdetect # Suggested by EC, https://pypi.org/project/langdetect/
from langdetect import DetectorFactory
DetectorFactory.seed = 0 # To enforce consistent results

# class LanguageDetectorLangdetect:
class LanguageDetector:
    def __init__(self):
        self.logger = logging.getLogger("Language detector")

    def predict_lang(self, text):
        # We want to get main language of a long text.
        try:
            detected_lang = langdetect.detect(text)
            # cut off region code
            detected_lang = detected_lang[0:2]
        except Exception as e:
            detected_lang = None
        return detected_lang
        # ga added by copying from ilsp-fc to C:\ProgramData\Anaconda3\envs\p3.8torch\Lib\site-packages\langdetect\profiles


class LanguageDetectorFasttext:
# class LanguageDetector:
    def __init__(self):
        self.logger = logging.getLogger("Language detector")
        pretrained_lang_model = "modules/lid.176.ftz"
        # pretrained_lang_model = "modules/lid.176.bin" # Supposedly better model, but fails to detect croatian test
        self.model = fasttext.load_model(pretrained_lang_model)

    def predict_lang(self, text):
        # We want to get main language of a long text.
        try:
            text_lines = text.split('\n')
        except AttributeError as e:
            self.logger.debug("Failed to split text {} into lines. Exception was: {}:".format(text, e))
            text_lines = []

        langs = {} # langs is a dict containing lang:lines_in_that_lang
        for text_line in text_lines:
            if not text_line.strip():
                continue
            predictions = self.model.predict(text_line, k=3) # returns top k matching languages
            most_likely_label = ''
            try:
                most_likely_label = predictions[0][0]
            except Exception as e:
                self.logger.debug("Failed prediction: {}".format(e))
            prediction = most_likely_label.replace('__label__', '')
            langs[prediction] = langs.get(prediction, 0) + 1

        try:
            lang_with_most_lines = max(langs, key=langs.get)
        except ValueError as e:
            self.logger.debug("Failed prediction: {}, Text given was:".format(e))
            self.logger.debug("{}".format(text))
            lang_with_most_lines = None
        return lang_with_most_lines

