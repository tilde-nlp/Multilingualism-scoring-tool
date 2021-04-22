Format - Dockers  
Interface - web forma   
Crawler - Scrapy  
Boilerplate - justext/trafilatura/html_text  
Lang detect - langdetect/fasttext   
Glue code - python  

Input list of domain names (possibly as file)  
Output list of scores (possibly as file) + detailed report  


# Dependencies
pip install scrapy  
pip install tldextract  
pip install justext OR pip install trafilatura OR pip install html_text  for text extraction/boilerplate removal  
pip install langdetect OR pip install pybind11 + pip install fasttext   

python=3.9.4
Scrapy-2.5.0
tldextract-3.1.0
jusText-2.2.0
trafilatura-0.8.2
html_text-0.5.2
langdetect-1.0.8

# Additional note 
Langdetect needs irish, maltese and korean model files updated:  
copy files from "dist\langdetect\profiles\"  
to folder where langdetect is installed in your system.  
On windows it will be something like  
"C:\ProgramData\Anaconda3\envs\python3.8\Lib\site-packages\langdetect\profiles\"