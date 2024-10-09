FROM python:3.10.12-alpine3.18

RUN pip install --upgrade pip
# USER ROOT
WORKDIR /opt/code
ADD ./code /opt/code/
ADD ./requirements.txt /opt/requirements.txt

RUN pip install -r /opt/requirements.txt