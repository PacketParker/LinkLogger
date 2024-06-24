FROM python:3.11-slim

LABEL org.opencontainers.image.source = "https://github.com/PacketParker/LinkLogger"

MAINTAINER "parker <mailto:contact@pkrm.dev>"

WORKDIR /

COPY . .
RUN pip install -r requirements.txt

ENTRYPOINT [ "python" ]
CMD [ "-u",  "linklogger.py" ]