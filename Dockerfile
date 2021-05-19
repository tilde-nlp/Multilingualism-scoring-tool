FROM python:3.9-buster

WORKDIR /scoring_tool_git

COPY . .
COPY ./dist/langdetect/profiles/ /usr/local/lib/python3.9/site-packages/langdetect/profiles/

RUN pip3 install -r requirements.txt

#ENTRYPOINT ["sh", "-c", "python3 app.py"]
CMD ["python3", "./app.py"]

