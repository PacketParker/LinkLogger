import jsonschema
import os
import yaml
import sys
import logging
from colorlog import ColoredFormatter

log_level = logging.DEBUG
log_format = (
    "  %(log_color)s%(levelname)-8s%(reset)s |"
    " %(log_color)s%(message)s%(reset)s"
)

logging.root.setLevel(log_level)
formatter = ColoredFormatter(log_format)

stream = logging.StreamHandler()
stream.setLevel(log_level)
stream.setFormatter(formatter)

LOG = logging.getLogger("pythonConfig")
LOG.setLevel(log_level)
LOG.addHandler(stream)

IP_TO_LOCATION = None
API_KEY = None

schema = {
    "type": "object",
    "properties": {
        "config": {
            "type": "object",
            "properties": {
                "ip_to_location": {"type": "boolean"},
                "api_key": {"type": "string"},
            },
            "required": ["ip_to_location"],
        }
    },
    "required": ["config"],
}


# Load config file or create new template
def load_config():
    if os.path.exists("/.dockerenv"):
        file_path = "/data/config.yaml"
    else:
        file_path = "config.yaml"

    try:
        with open(file_path, "r") as f:
            file_contents = f.read()
            validate_config(file_contents)

    except FileNotFoundError:
        # Create new config.yaml w/ template
        with open(file_path, "w") as f:
            f.write(
                """
config:
    ip_to_location:
    api_key:"""
            )
        LOG.critical(
            "`config.yaml` was not found, a template has been created."
            " Please fill out the necessary information and restart."
        )
        sys.exit()


# Validate the options within config.yaml
def validate_config(file_contents):
    global IP_TO_LOCATION, API_KEY
    config = yaml.safe_load(file_contents)

    try:
        jsonschema.validate(config, schema)
    except jsonschema.ValidationError as e:
        LOG.error(e.message)
        sys.exit()

    # Make IP_TO_LOCATION a boolean
    IP_TO_LOCATION = bool(config["config"]["ip_to_location"])

    # Validate API_KEY if IP_TO_LOCATION is set to TRUE
    if IP_TO_LOCATION:
        if not config["config"]["api_key"]:
            LOG.error("API_KEY is not set")
        else:
            API_KEY = config["config"]["api_key"]
