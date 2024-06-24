import configparser
import validators
import os
import sys

from var import LOG

"""
Validate the config of a Docker run (environment variables)
"""


def validate_docker_config():
    errors = 0

    # Validate BASE_URL
    try:
        if not os.environ["BASE_URL"]:
            LOG.error("BASE_URL is not set")
            errors += 1
        elif not validators.url(os.environ["BASE_URL"]):
            LOG.error("BASE_URL is not a valid URL")
            errors += 1
    except KeyError:
        LOG.critical("BASE_URL does not exist!")
        errors += 1

    # Validate IP_TO_LOCATION
    try:
        if not os.environ["IP_TO_LOCATION"]:
            LOG.error("IP_TO_LOCATION is not set")
            errors += 1
        elif os.environ["IP_TO_LOCATION"].upper() not in ["TRUE", "FALSE", "T", "F"]:
            LOG.error("IP_TO_LOCATION is not set to TRUE or FALSE")
            errors += 1
        else:
            iptolocation = (
                True if os.environ["IP_TO_LOCATION"].upper() in ["TRUE", "T"] else False
            )
            # Validate API_KEY if IP_TO_LOCATION is set to TRUE
            if iptolocation:
                try:
                    if not os.environ["API_KEY"]:
                        LOG.error("API_KEY is not set")
                        errors += 1
                except KeyError:
                    LOG.critical("API_KEY does not exist!")
                    errors += 1
    except KeyError:
        LOG.critical("IP_TO_LOCATION does not exist!")
        errors += 1

    if errors > 0:
        LOG.critical(f"{errors} error(s) found in environment variables")
        sys.exit()


"""
Validate the config of a bare metal run (config.ini file)
"""


def validate_bare_metal_config(file_contents):

    config = configparser.ConfigParser()
    config.read_string(file_contents)

    errors = 0

    # Validate BASE_URL
    try:
        if not config["CONFIG"]["BASE_URL"]:
            LOG.error("BASE_URL is not set")
            errors += 1
        elif not validators.url(config["CONFIG"]["BASE_URL"]):
            LOG.error("BASE_URL is not a valid URL")
            errors += 1
    except ValueError:
        LOG.critical("BASE_URL does not exist!")
        errors += 1

    # Validate IP_TO_LOCATION
    try:
        if not config["CONFIG"]["IP_TO_LOCATION"]:
            LOG.error("IP_TO_LOCATION is not set")
            errors += 1
        elif config["CONFIG"]["IP_TO_LOCATION"].upper() not in [
            "TRUE",
            "FALSE",
            "T",
            "F",
        ]:
            LOG.error("IP_TO_LOCATION is not set to TRUE or FALSE")
            errors += 1
        else:
            iptolocation = (
                True
                if config["CONFIG"]["IP_TO_LOCATION"].upper() in ["TRUE", "T"]
                else False
            )
        # Validate API_KEY if IP_TO_LOCATION is set to TRUE
        if iptolocation:
            try:
                if not config["CONFIG"]["API_KEY"]:
                    LOG.error("API_KEY is not set")
                    errors += 1
            except ValueError:
                LOG.critical("API_KEY does not exist!")
                errors += 1
    except ValueError:
        LOG.critical("IP_TO_LOCATION does not exist!")
        errors += 1

    if errors > 0:
        LOG.critical(f"{errors} error(s) found in `config.ini`")
        sys.exit()


def validate_config():
    # If the app is running in Docker
    if "BASE_URL" in os.environ or "IP_TO_LOCATION" in os.environ:
        return validate_docker_config()

    # Otherwise, the app is running on bare metal
    try:
        with open("config.ini", "r") as f:
            file_contents = f.read()
            return validate_bare_metal_config(file_contents)
    except FileNotFoundError:
        config = configparser.ConfigParser()
        config["CONFIG"] = {"BASE_URL": "", "IP_TO_LOCATION": "", "API_KEY": ""}

        with open("config.ini", "w") as configfile:
            config.write(configfile)

        LOG.error(
            "`config.ini` has been created. Fill out the necessary information then re-run."
        )
        sys.exit()
