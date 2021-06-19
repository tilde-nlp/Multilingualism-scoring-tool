import re
import logging
# pip install tldextract # BSD 3-Clause License # https://github.com/john-kurkowski/tldextract/blob/master/LICENSE
import tldextract
# pip install jusText # BSD 2-Clause License # https://pypi.org/project/jusText/
import justext 
# from trafilatura.core import extract
# import html_text


def is_ok_job_name(job_name:str) -> bool:
    if not job_name.strip():
        return False
    if all(x.isalnum() or x.isspace() or x in '.' for x in job_name):
        return True
    else:
        return False

def extractDomain(url):
    if "http" in str(url) or "www" in str(url):
        parsed = tldextract.extract(url)
        # parsed = ExtractResult(subdomain='', domain='', suffix='')
        # Note subdomain and suffix are optional. 
        # parts = [parsed.subdomain, parsed.domain, parsed.suffix]
        parts = [parsed.domain, parsed.suffix]
        domain = ".".join([i for i in parts if i])
        return domain
    return None

def segmentText(text):
    """Simple 'sentence' splitter. 
    Returns the input text with newlines inserted and empty lines removed. """
    try:
        segments = re.findall(r'(.*?[:?!.۔܁።᙮᠃᠉⳾。︒﹒．｡;՞؟፧⁈⁉︖﹖？՜︕﹗！]\s+)', text)
    except TypeError as e:
        logger = logging.getLogger("segmentText")
        logger.debug("{}".format(e))
        return text
    segments = [segment.strip() for segment in segments if segment.strip()]
    segmented_text = '\n'.join(segments)
    return segmented_text



# def extractTextXPath(response):
#     text = response.xpath('//body//text()').extract()
#     text = ' '.join(text)
#     text = text.replace('  ',' ')
#     text_lines = text.split('\n')
#     text_lines = [text_line.strip() for text_line in text_lines if text_line.strip()]
#     text = '\n'.join(text_lines)
#     return text

# justext
# def extractTextJustext(response):
def extractText(response):
    text_lines = []
    paragraphs = justext.justext(response.text, frozenset(), stopwords_low=10,stopwords_high=0)
    for paragraph in paragraphs:
        # print("Paragraph is boilerplate:{}; {}".format(paragraph.is_boilerplate, paragraph.text))
        if not paragraph.is_boilerplate:
            text_lines.append(paragraph.text)
    text = '\n'.join(text_lines)
    return text
    

# # https://github.com/adbar/trafilatura
# # Good F1 measure
# def extractText_trafilatura(response):
#     text = extract(response.text, response.url)
#     text = segmentText(text)
#     if text is None:
#         return ""
#     return text

# # https://pypi.org/project/html-text/
# # Excellent recall (basically, all text)
# def extractTextHtml2Text(response):
#     text = html_text.extract_text(response.text)
#     text = segmentText(text)
#     return text
#     # >>> html_text.extract_text('<h1>Hello</h1> world!')
#     # 'Hello\n\nworld!'
#     # >>> html_text.extract_text('<h1>Hello</h1> world!', guess_layout=False)
#     # 'Hello world!'