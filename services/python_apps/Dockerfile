FROM python:alpine3.9

# USER ROOT
WORKDIR /opt/code

ADD ./code /opt/code/
ADD ./requirements.txt /opt/requirements.txt

RUN pip install -r /opt/requirements.txt