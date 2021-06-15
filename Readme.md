# About Multilingualism Scoring Tool 
The Multilingualism Scoring Tool analyses web sites based on the contents and languages used in their web pages. 
The tool crawls each site page by page, extracts its contents, detects the language of each page and other language related relevant data. 
Lastly, it creates some statistics and calculates multilingualism scores based on the data and statistics obtained.

Format - Docker  
Interface - web form   
Crawler - Scrapy  
Boilerplate - justext  
Language detector - langdetect   
Glue code - python 3.9 

Input: list of URLs (both as text input, and simple txt file)  
Output: list of scores (on website) + download simple and detailed csv  


# Dependencies
pip install scrapy==2.5.0  
pip install tldextract==3.1.0  
pip install justext==2.2.0  
pip install langdetect==1.0.8   
pip install tornado==6.1  

# Additional notes 
The tool and some tests do not run on Windows due to different implementation of multiprocessing from Linux. 
On Windows WSL (Windows Subsystem for Linux) may be used to launch the tool from command line.

Langdetect needs irish, maltese and korean model files updated:  
copy files from "dist\langdetect\profiles\"  
to folder where langdetect is installed in your system.  
On linux it will be something like  
"/usr/local/lib/python3.9/site-packages/langdetect/profiles/"

# Run the tool
- From Linux command line: "python app.py" starts the web service.
- Using docker build (on local machine): 
	- docker build --tag scorer . --no-cache 
	- docker run -p 8989:8989 -t scorer 
	- tool then may be accessed on http://localhost:8989/score
- Alternative using github packages: 
	- docker pull ghcr.io/tilde-nlp/multilingualism-scoring-tool:master 
	- docker run -p 8989:8989 -t ghcr.io/tilde-nlp/multilingualism-scoring-tool:master  
 	- tool then may be accessed on http://localhost:8989/score 
- Tests may be run using command "python -m unittest discover -s tests" 
- Test with offline websites may be run using command "python test_all_sites.py" . Note that to test on offline websites, these offline websites must be preseont in tests\offline_sites\ folder. 

