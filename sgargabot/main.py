import discord
import logging

import utils.config as config
from utils.logging import initialize_logging
from models.enums import LogLevel

logger = logging.getLogger(__name__)

def main():
    client = discord.Client()
    initialize_logging(LogLevel.from_str(config.LOG_LEVEL), config.LOG_FILENAME, config.LOG_FOLDER)
    cfg = config.BotConfig()
    print(config.ALL_EXTENSIONS)
    #client.run(config.BOT_TOKEN)

if __name__ == "__main__":
    main()
