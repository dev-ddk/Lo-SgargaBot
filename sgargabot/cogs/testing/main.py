import logging
import discord
import datetime

from discord.ext import commands

from sgargabot.core.decorators import (
    callable_once,
    callable_n_times,
    callable_once_within,
    callable_once_per_day,
)

logger = logging.getLogger(__name__)


class Gambling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="slotmachine", aliases=["slot"])
    @callable_once_within(datetime.timedelta(hours=1))
    async def slotmachine(self, ctx):
        await ctx.send("You only have five calls!")

    @slotmachine.error
    async def slotmachine_error(self, ctx, error):
        logger.info(error)
        await ctx.send(
            f"Sorry bro! You can only call this command once every ten seconds. Time before you can call this function: {error.original.get_remaining_time()}"
        )


def setup(bot):
    bot.add_cog(Gambling(bot))
