
# LinkLogger API

A simple API for you to create redirect links on my domain (link.pkrm.dev) and log all IPs that click on the link. Essentially just grabify with no GUI.

Feel free to submit an issue for any problems you experience or if you have an idea for a new feature. If you have a fix for anything, please submit a pull request for review.

## Want to self-host?

#### Bare metal
Feel free to fork this code and run it yourself, simply install the dependencies, create your `.env` file and run the `linklogger.py` file.

#### Docker
Use the docker-compose below as an example of running LinkLogger in docker.
```yaml
version: '3.3'
services:
    linklogger:
        container_name: linklogger
        image: packetparker/linklogger
        network_mode: host
        environment:
            - BASE_URL=https://your.domain
            - IP_TO_LOCATION=True
            - API_KEY=Your Key
        volumes:
            - /local/file/path:/data
        restart: unless-stopped
```
Variable | Description | Requirement
---|---|---
BASE_URL | Redirect link for when people visit old/dead/non-existant link | **Required**
IP_TO_LOCATION | "True"/"False" Whether or not you want to IP to Location feature (requires IP2Location.io account)  | **Required**
API_KEY | IP2Location.io API Key | **Required** *unless IP_TO_LOCATION is "False"*

## API Reference

#### View the API reference and try out the endpoints at the [docs page](https://link.pkrm.dev/docs)