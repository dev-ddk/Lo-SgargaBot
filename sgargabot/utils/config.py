from decouple import config
import os
import json
import logging
import datetime

from zoneinfo import ZoneInfo

from sgargabot.models.enums import LogLevel

logger = logging.getLogger(__name__)

# Environment Variables

BOT_TOKEN = config("BOT_TOKEN")
CONFIG_FOLDER = config("CONFIG_FOLDER", default="config/")
CONFIG_FILE = config("CONFIG_FILE", default="config.json")
TIMEZONE = config("TIMEZONE", default="Europe/Rome")

## Logging Env Vars

LOG_LEVEL = config("LOG_LEVEL", default="WARNING", cast=LogLevel.from_str)
LOG_FOLDER = config("LOG_FOLDER", default="logs/")
LOG_FILENAME = "sgargabot.log"

## MongoDB Env Vars

MONGODB_HOST = config("MONGODB_HOST", default="127.0.0.1")
MONGODB_PORT = config("MONGODB_PORT", cast=int, default=27017)
MONGODB_MAIN = "sgargabot"  # Main DB to use
MONGODB_USER = config("MONGODB_USER")
MONGODB_PASSWORD = config("MONGODB_PASSWORD")

# Utility vars

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COGS_DIR = os.path.join(BASE_DIR, "sgargabot/cogs")

TZ_ZONEINFO = ZoneInfo(TIMEZONE)

PREFIX = "$"
DESCRIPTION = "Nelle notti senza luna, starnutendo davanti ad uno specchio, c'è una probabilità del 5% che Achille Frigeri balzi fuori da una cassapanca lì vicina"

# Base Classes


class Singleton(type):
    """Singleton metaclass

    A metaclass implementing the Singleton pattern, allowing only one instance with type `type` to exist.
    """

    _instances: dict[type, object] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


# Configuration for the Bot's Functionalities


class BotConfig(metaclass=Singleton):
    """Bot Configuration Class

    A class which is used to store the runtime configuration for the Bot.
    The file indicated by the environment variables CONFIG_FOLDER and CONFIG_FILE are used to locate the configuration file.
    After reading the file, configuration values can be accessed as attributes, with the corresponding key in uppercase and with spaces replaced by underscores.
    Attributes should be treated as read-only. No guarantees on concurrency are given when trying to programmatically change the values of attributes.
    Start-up configuration should be given as environment variables.
    """

    def __init__(self):
        self._config_folder = (
            CONFIG_FOLDER
            if os.path.isabs(CONFIG_FOLDER)
            else os.path.join(BASE_DIR, CONFIG_FOLDER)
        )
        self._load_config()

    def _load_config(self):
        config_file = os.path.join(self._config_folder, CONFIG_FILE)
        try:
            with open(config_file) as config:
                self._config = json.loads(config.read())
        except FileNotFoundError:
            logger.error(f"Could not open the config file at {config_file}")
            logger.error(f"Exception raised", exc_info=True)
        self.__dict__.update(
            {k.replace(" ", "_").upper(): v for k, v in self._config.items()}
        )

    def reload(self):
        self._load_config()
