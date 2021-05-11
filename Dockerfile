FROM python:3.9-buster

WORKDIR /scoring_tool_git

COPY . .

RUN pip3 install -r requirements.txt

#ENTRYPOINT ["sh", "-c", "python3 app.py"]
CMD ["python3", "./app.py"]

