FROM python:3.9-buster

WORKDIR /scoring_tool_git

COPY . .

RUN pip3 install -r requirements.txt

ENTRYPOINT ["sh", "-c", "python3 app.py"]


#COPY requirements.txt /ner-web-app/
#RUN pip3 install -r /ner-web-app/requirements.txt
#
##RUN python3 -c "import stanza; stanza.download('en')"
#RUN python3 -c "import stanza; stanza.download('lv')"
#
#COPY saved_model /ner-web-app/saved_model
#COPY scripts /ner-web-app/scripts
##COPY resources /ner-web-app/resources
#
#WORKDIR /ner-web-app
#
#ENV lang="lv"
#ENV saved_model_dir="./saved_model/"
#ENV port="8899"
#
#ENTRYPOINT ["sh", "-c", "python3 scripts/NERApp.py ${lang} ${saved_model_dir} ${port}"]
