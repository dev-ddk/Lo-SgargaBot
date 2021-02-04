from decouple import config
import os
import json
import logging

# Environment Variables

BOT_TOKEN = config('BOT_TOKEN')
CONFIG_FOLDER = config('CONFIG_FOLDER', default='config/')
CONFIG_FILE = config('CONFIG_FILE', default='config.json')
LOG_LEVEL = config('LOG_LEVEL', default='WARNING')
LOG_FOLDER = config('LOG_FOLDER', default='logs/')
LOG_FILENAME = 'sgargabot.log'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COGS_DIR = os.path.join(BASE_DIR, 'sgargabot/cogs')

ALL_EXTENSIONS = ['cogs.'+f+'.main' for f in next(os.walk(COGS_DIR))[1]]

logger = logging.getLogger(__name__)

# Base Classes

class Singleton(type):
    """Singleton metaclass

    A metaclass implementing the Singleton pattern, allowing only one instance with type `type` to exist.
    """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

# Configuration for the Bot's Functionalities

class BotConfig(metaclass=Singleton):
    """Bot Configuration Class

    A class which is used to store the configuration for the Bot.
    The file indicated by the environment variables CONFIG_FOLDER and CONFIG_FILE are used to locate the configuration file.
    After reading the file, configuration values can be accessed as attributes, with the corresponding key in uppercase and with spaces replaced by underscores.
    Attributes should be treated as read-only. No guarantees on concurrency are given when trying to programmatically change the values of attributes.
    """

    def __init__(self):
        self._config_folder = CONFIG_FOLDER if os.path.isabs(CONFIG_FOLDER) else os.path.join(BASE_DIR, CONFIG_FOLDER)
        self._load_config()

    def _load_config(self):
        config_file = os.path.join(self._config_folder, CONFIG_FILE)
        try:
            with open(config_file) as config:
                self._config = json.loads(config.read())
        except FileNotFoundError:
            logger.error(f'Could not open the config file at {config_file}')
            logger.error(f'Exception raised', exc_info=True)
        self.__dict__.update({k.replace(' ', '_').upper(): v for k, v in self._config.items()})

    def reload(self):
        self._load_config()
