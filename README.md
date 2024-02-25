
# LinkLogger API

A simple API for you to create redirect links on my domain (link.pkrm.dev) and log all IPs that click on the link. Essentially a CLI-only version of Grabify.

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
        ports:
            - 5252:5252
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

#### Create account/api key
##### Your account name functions as your API key and will only be provided to you once.
```http
GET /signup
```
```curl
curl https://link.pkrm.dev/signup
```

#### Create new link
##### Creates a randomized short link that will redirect to the link you provide while logging the IP of the visitor
```http
POST /newlink
```
```curl
curl -X POST \
    -H "Content-type: application/json" \
    -H "Authorization: Bearer YOUR_ACCOUNT_NAME" \
    -d '{"redirect_link": "YOUR_LINK_OF_CHOICE"}' \
    https://link.pkrm.dev/newlink
```

#### Get all links
##### Retrieve all of the links and their expiry dates associated with your account
```curl
curl -X POST \
    -H "Authorization: Bearer YOUR_ACCOUNT_NAME" \
    https://link.pkrm.dev/links
```

#### Get all logs
##### Retrieve all IP logs associated with every link on your account
```http
POST /records
```
```curl
curl -X POST \
    -H "Authorization: Bearer YOUR_ACCOUNT_NAME" \
    https://link.pkrm.dev/records
```

#### Delete link
##### Delete the specified link as well as all records associated with it
```http
POST /<link>/records
```
```curl
curl -X POST \
    -H "Authorization: Bearer YOUR_ACCOUNT_NAME" \
    https://link.pkrm.dev/<link>/delete
```

#### Renew link
##### Add 7 more days (from the current date) to the expiry value of the link
```http
POST /<link>/Renew
```
```curl
curl -X POST \
    -H "Authorization: Bearer YOUR_ACCOUNT_NAME" \
    https://link.pkrm.dev/<link>/renew
```

#### Link records
##### Retrieve all IP logs associated with the link
```http
POST /<link>/records
```
```curl
curl -X POST \
    -H "Authorization: Bearer YOUR_ACCOUNT_NAME" \
    https://link.pkrm.dev/<link>/records
```

