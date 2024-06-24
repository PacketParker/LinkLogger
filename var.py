import configparser
import logging
import os
from colorlog import ColoredFormatter


log_level = logging.DEBUG
log_format = "%(log_color)s%(levelname)-8s%(reset)s  %(log_color)s%(message)s%(reset)s"

logging.root.setLevel(log_level)
formatter = ColoredFormatter(log_format)

stream = logging.StreamHandler()
stream.setLevel(log_level)
stream.setFormatter(formatter)

LOG = logging.getLogger("pythonConfig")
LOG.setLevel(log_level)
LOG.addHandler(stream)


# If the app is running in Docker
if "BASE_URL" in os.environ or "IP_TO_LOCATION" in os.environ:
    BASE_URL = os.environ["BASE_URL"]
    IP_TO_LOCATION = (
        True if os.environ["IP_TO_LOCATION"].upper() in ["TRUE", "T"] else False
    )
    if IP_TO_LOCATION:
        API_KEY = os.environ["API_KEY"]
    else:
        API_KEY = None

# Otherwise, the app is running on bare metal
try:
    with open("config.ini", "r") as f:
        config = configparser.ConfigParser()
        config.read_string(f.read())

        BASE_URL = config["CONFIG"]["BASE_URL"]
        IP_TO_LOCATION = (
            True
            if config["CONFIG"]["IP_TO_LOCATION"].upper() in ["TRUE", "T"]
            else False
        )
        if IP_TO_LOCATION:
            API_KEY = config["CONFIG"]["API_KEY"]
        else:
            API_KEY = None
except FileNotFoundError:
    config = configparser.ConfigParser()
    config["CONFIG"] = {"BASE_URL": "", "IP_TO_LOCATION": "", "API_KEY": ""}

    with open("config.ini", "w") as configfile:
        config.write(configfile)

    LOG.error(
        "`config.ini` has been created. Fill out the necessary information then re-run."
    )
    exit()
