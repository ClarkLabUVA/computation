FROM ubuntu:latest

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

RUN pip install kubernetes
RUN pip install flask
RUN pip install minio
RUN pip install uwsgi
RUN pip install pyjwt

COPY . .
COPY compute_class.py .

ENTRYPOINT [ "uwsgi", "--ini", "http.ini"]
