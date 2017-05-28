FROM python:3-alpine

RUN pip install influxdb

ADD CyberpowerUpsStats.py /stats.py
ADD config.ini /config.ini

CMD ["/stats.py"]
