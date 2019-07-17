FROM python:3.7-slim-stretch

RUN adduser --disabled-password --gecos '' myflask

WORKDIR /home/myflask

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt

COPY app.py config.py sqreen.ini ./
COPY myapp myapp

ENV FLASK_APP app.py

USER myflask

EXPOSE 5000
CMD ["venv/bin/gunicorn", "-b", ":5000", "--access-logfile", "-", "--error-logfile", "-", "app:app"]