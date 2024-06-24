<h1 align="center">
    LinkLogger
</h1>

<h3 align="center">
    Link shortener and IP logger
</h3>

<p align="center">
    <a href="https://github.com/psf/black">
        <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code Style: Black">
    </a>
    <a href="https://makeapullrequest.com">
        <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg">
    </a>
</p>

# Overview
### Create an account now at [link.pkrm.dev](https://link.pkrm.dev/signup)

<br>

LinkLogger is simple and public API to create redirect links and log IPs. Every visit to a registered short link will log the users IP address, location, user agent, browser, and OS before redirecting them to a specific URL.

Just like Grabify, but unrestricted and with no real web UI.

Feel free to submit an issue for any problems you experience or if you have an idea for a new feature. If you have a fix for anything, feel free to submit a pull request for review.

# API Reference
View the API reference and try out the endpoints at the [docs page](https://link.pkrm.dev/api/docs)

# Want to self-host?

## Bare metal
To run LinkLogger on bare metal, follow the steps below.

*NOTE: For information on each configuration variable, look at the `Configuration` section of this page.*

1. Install Python and Pip
2. Clone this repository
3. Install the requirements with `pip install -r requirements.txt`
4. Run the `linklogger.py` file
5. Input information into the newly created `config.ini` file.
6. Re-run the `linklogger.py` file.

## Docker
To run LinkLogger in Docker, use the [docker-compose.yaml](/docker-compose.yaml) as a template for the contianer.

## Config
Below are all of the configuration variables that are used within LinkLogger.

Variable | Description | Requirement
---|---|---
BASE_URL | `URL`: Redirect URL for when people visit old, dead, or non-existant links | **Required**
IP_TO_LOCATION | `BOOLEAN`:  Whether or not you want toe IP to Location feature <br> *(requires IP2Location.io account)* | **Required**
API_KEY | `KEY`: IP2Location.io API Key | **Required** *only if IP_TO_LOCATION is set to True*