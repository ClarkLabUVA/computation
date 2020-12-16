FROM ubuntu:latest

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

RUN apt-get install -y git

RUN pip install kubernetes
RUN pip install flask
RUN pip install minio
RUN pip install uwsgi
RUN pip install pyjwt
RUN echo hellloooo1
RUN pip3 install git+https://github.com/fairscape/python-auth

COPY . .
COPY compute_class.py .

ENTRYPOINT [ "uwsgi", "--ini", "http.ini"]
