import jsonschema
import os
import yaml
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
DB_NAME = None
DB_ENGINE = None
DB_HOST = None
DB_PORT = None
DB_USER = None
DB_PASSWORD = None

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
        },
        "database": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "default": "linklogger"},
                "engine": {"type": "string"},
                "host": {"type": "string"},
                "port": {"type": "integer"},
                "user": {"type": "string"},
                "password": {"type": "string"},
            },
            "required": [
                "name",
                "engine",
                "host",
                "port",
                "user",
                "password",
            ],
        },
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
            if not validate_config(file_contents):
                return False
            else:
                return True

    except FileNotFoundError:
        # Create new config.yaml w/ template
        with open(file_path, "w") as f:
            f.write(
                """config:
    ip_to_location: false
    api_key: ''

database:
    engine: 'sqlite'
    name: ''
    host: ''
    port: 0
    user: ''
    password: ''"""
            )
        LOG.critical(
            "`config.yaml` was not found, a template has been created."
            " Please fill out the necessary information and restart."
        )
        return False


# Validate the options within config.yaml
def validate_config(file_contents):
    global IP_TO_LOCATION, API_KEY, DB_NAME, DB_ENGINE, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD
    config = yaml.safe_load(file_contents)

    try:
        jsonschema.validate(config, schema)
    except jsonschema.ValidationError as e:
        LOG.error(e.message)
        return False

    # Make IP_TO_LOCATION a boolean
    IP_TO_LOCATION = bool(config["config"]["ip_to_location"])

    # Validate API_KEY if IP_TO_LOCATION is set to TRUE
    if IP_TO_LOCATION:
        if not config["config"]["api_key"]:
            LOG.error("API_KEY is not set")
            return False
        else:
            API_KEY = config["config"]["api_key"]

    #
    # Set/Validate the DATABASE section of the config.yaml
    #
    if "database" in config:
        if config["database"]["engine"] not in [
            "sqlite",
            "mysql",
            "postgresql",
        ]:
            LOG.error(
                "database_engine must be either 'sqlite', 'mysql', or"
                " 'postgresql'"
            )
            return False
        else:
            DB_ENGINE = config["database"]["engine"]

        DB_NAME = config["database"]["name"]
        DB_HOST = config["database"]["host"]
        DB_PORT = config["database"]["port"]
        DB_USER = config["database"]["user"]
        DB_PASSWORD = config["database"]["password"]

    return True
