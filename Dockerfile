FROM tiangolo/uwsgi-nginx-flask:python3.6

WORKDIR /app/

COPY requirements.txt /app/
RUN pip install -r ./requirements.txt

ENV LISTEN_PORT 5000
EXPOSE 5000

ENV ENVIRONMENT local

COPY main.py __init__.py /app/
