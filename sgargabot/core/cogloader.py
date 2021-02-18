import os
import logging

from discord.ext import commands

import sgargabot.utils.config as config
from sgargabot.models.exceptions import InexistentCogError

logger = logging.getLogger(__name__)


class LoadedCogs:
    def __init__(self, bot: commands.Bot):
        self.load_cogs(bot)

    def load_cogs(self, bot: commands.Bot):
        self.loaded_cogs = {}
        logger.info("Loading extensions")
        cfg = config.BotConfig()
        all_cogs = self.get_all_cogs()
        for cog_name, cog in all_cogs.items():
            if cog_name not in cfg.DISABLED_COGS:
                logger.info(f"Loading extension {cog_name}")
                bot.load_extension(cog)
                self.loaded_cogs.update({cog_name: cog})

        logger.info("Finished loading extensions")

    def get_all_cogs(self):
        all_cogs = {}
        for f in next(os.walk(config.COGS_DIR))[1]:
            if "main.py" in os.listdir(os.path.join(config.COGS_DIR, f)):
                cog_name = "cogs." + f + ".main"
                logger.info("Found loadable cog: {cog_name}")
                all_cogs.update({f: cog_name})
        return all_cogs

    def reload_cog(self, cog_name: str):
        if cog_name not in self.load_cogs:
            raise InexistentCogError(cog_name)
