import logging
import discord
import datetime
from discord.ext import commands

from sgargabot.core.decorators import callable_once, callable_n_times

logger = logging.getLogger(__name__)




class Gambling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='slotmachine', aliases=['slot'])
    @callable_n_times(5)
    async def slotmachine(self, ctx):
        await ctx.send("You only have five calls!")

    @slotmachine.error
    async def slotmachine_error(self, ctx, error):
        logger.info(error)
        await ctx.send("Sorry bro! You can only call this command five times in your lifetime")


def setup(bot):
    bot.add_cog(Gambling(bot))

