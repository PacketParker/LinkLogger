FROM node:18-slim AS build-ui

WORKDIR /app
COPY app/ ./
RUN yarn install
RUN yarn build

FROM python:3.11-slim AS api

LABEL org.opencontainers.image.source="https://github.com/PacketParker/LinkLogger"
LABEL maintainer="parker <mailto:contact@pkrm.dev>"

WORKDIR /
COPY . .
RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y nginx && \
    rm -rf /var/lib/apt/lists/*

# Move the built files into the nginx share
COPY --from=build-ui /app/dist /usr/share/nginx/html
# Replace the default site with the LinkLogger config
COPY nginx.conf /etc/nginx/sites-enabled/default

CMD service nginx start && python -u linklogger.py