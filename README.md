<h1 align="center">LinkLogger</h1>

<h3 align="center">Link Shortener and IP Logger</h3>

<p align="center">
    <a href="https://github.com/psf/black">
        <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code Style: Black">
    </a>
    <a href="https://makeapullrequest.com">
        <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome">
    </a>
    <a href="https://ghcr.io/packetparker/linklogger">
        <img src="https://img.shields.io/docker/v/packetparker/linklogger?label=Docker" alt="Docker">
    </a>
</p>

# Overview

### Create an account at [link.pkrm.dev/signup](https://link.pkrm.dev/signup)

**LinkLogger** is an *extremely* simple and public link shortener and IP logger. Every visit to a registered short link will log the user's IP address, location, user agent, browser, and OS before redirecting them to a specific URL.

The API is built on **FastAPI**, and the UI is built with **React**.
*NOTE:* I am NOT a front-end dev, so don't expect much on that. 😅

Feel free to submit an issue for any problems you experience or if you have an idea for a new feature. If you have a fix for anything, feel free to submit a pull request for review.

**TL;DR:** LinkLogger is like Grabify, but unrestricted and with a rudimentary UI.

# API Reference

You can view the full **API reference** and try out the endpoints on the [docs page](https://link.pkrm.dev/docs).

# Want to Self-Host?
## Docker

Docker is the recommended method of hosting LinkLogger. Running on bare metal is recommended for development.

To run LinkLogger on Docker, check out the [docker-compose.yaml](docker-compose.yaml) file.

## Bare metal

If you want to work on the LinkLogger source, or just want to run the project on bare metal, follow the instructions below:

1. Install python3.10 & pip (other python versions may work, but are currently untested)
2. Install Node.js
3. Install Yarn
4. Install API dependencies (pip install -r requirements.txt)
5. Run either [linklogger.sh](linklogger.sh) (Linux/MacOS) or [linklogger.bat](linklogger.bat) (Windows)

*NOTE: Running on bare metal means there is not an NGINX instance to serve the UI and proxy API requests to port 5252.*

## Configuration

Below are all of the configuration variables that are used within the LinkLogger config.yaml file.

| **Variable**        | **Description**  | **Requirement** |
|---------------------|------------------|-----------------|
| `IP_TO_LOCATION`    | `BOOLEAN`: Whether or not you want the IP-to-Location feature. *(requires IP2Location.io account)* | **Required** |
| `API_KEY`           | `API KEY`: IP2Location.io API Key | **Required** (only if `IP_TO_LOCATION` is set to `True`) |