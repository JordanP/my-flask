FROM python:3.6

RUN adduser --disabled-password myflask

WORKDIR /home/myflask

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt

COPY app.py config.py start.sh sqreen.ini ./
COPY myapp myapp

ENV FLASK_APP app.py

RUN chown -R myflask:myflask ./
USER myflask

EXPOSE 5000
ENTRYPOINT ["./start.sh"]