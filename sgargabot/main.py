import discord
import logging

from discord.ext import commands

import sgargabot.utils.config as config
from sgargabot.utils.logging import initialize_logging
from sgargabot.models.enums import LogLevel
from sgargabot.core.sgargabot import SgargaBot

logger = logging.getLogger(__name__)


def main():
    initialize_logging(config.LOG_LEVEL, config.LOG_FILENAME, config.LOG_FOLDER)
    sgargabot = SgargaBot()
    sgargabot.run()


if __name__ == "__main__":
    main()
