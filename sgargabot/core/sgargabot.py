import logging
import mongoengine
from discord.ext import commands

import sgargabot.utils.config as config
from sgargabot.core.cogloader import LoadedCogs

logger = logging.getLogger(__name__)

class SgargaBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        logger.warning("Lo Sgargabot is starting...")
        super().__init__(*args, **kwargs, command_prefix=config.PREFIX,
                         description=config.DESCRIPTION)
        self.loaded_cogs = LoadedCogs(self)
        self.db = mongoengine.connect(db=config.MONGODB_MAIN, host="mongodb://"+config.MONGODB_USER+":"+config.MONGODB_PASSWORD+"@"+config.MONGODB_HOST+":"+str(config.MONGODB_PORT)+"/?authSource=admin")

    def run(self):
        super().run(config.BOT_TOKEN, bot=True, reconnect=True)



