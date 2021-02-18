import logging
import mongoengine
from discord.ext import commands

import sgargabot.utils.config as config
from sgargabot.core.cogloader import LoadedCogs
from async_cron.schedule import Scheduler

logger = logging.getLogger(__name__)


class SgargaBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        logger.warning("Lo Sgargabot is starting...")
        super().__init__(
            *args,
            **kwargs,
            command_prefix=config.PREFIX,
            description=config.DESCRIPTION
        )
        self.scheduler = Scheduler(locale=config.SCHEDULER_LOCALE)
        self.loaded_cogs = LoadedCogs(self)
        self.db = mongoengine.connect(
            db=config.MONGODB_MAIN,
            host="mongodb://"
            + config.MONGODB_USER
            + ":"
            + config.MONGODB_PASSWORD
            + "@"
            + config.MONGODB_HOST
            + ":"
            + str(config.MONGODB_PORT)
            + "/?authSource=admin",
            tz_aware=True
        )
        self.loop.create_task(self.scheduler.start())

    def run(self):
        super().run(config.BOT_TOKEN, bot=True, reconnect=True)
