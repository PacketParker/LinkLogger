FROM python:3.11-slim

MAINTAINER "parker <mailto:contact@pkrm.dev>"

WORKDIR /

COPY . .
RUN pip install -r requirements.txt

ENTRYPOINT [ "python" ]
CMD [ "-u",  "app/linklogger.py" ]