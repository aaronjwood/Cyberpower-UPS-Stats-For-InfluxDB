FROM python:3-alpine

ADD requirements.txt /requirements.txt
ADD CyberpowerUpsStats.py /stats.py
ADD config.ini /config.ini

RUN pip install -r /requirements.txt

CMD ["/stats.py"]
