import logging
import discord
import datetime

from zoneinfo import ZoneInfo
from discord.ext import commands

from sgargabot.core.decorators import callable_once, callable_n_times, callable_once_within, callable_once_per_day

logger = logging.getLogger(__name__)




class Gambling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='slotmachine', aliases=['slot'])
    @callable_once_within(datetime.timedelta(seconds=5))
    async def slotmachine(self, ctx):
        await ctx.send("You only have five calls!")

    @commands.command(name='slutmachine', aliases=['slut'])
    @callable_once_per_day
    async def slutmachine(self, ctx):
        await ctx.send("You called my, babyyyy")

    @slutmachine.error
    async def slutmachine_error(self, ctx, error):
        logger.info(error, exc_info=True)
        await ctx.send(f"Sorry bro! You can only call this command once per day. Time before you can call this function {error.original.time_remaining}")

    @slotmachine.error
    async def slotmachine_error(self, ctx, error):
        logger.info(error, exc_info=True)
        await ctx.send(f"Sorry bro! You can only call this command two times every ten seconds. Time before you can call this function {error.original.time_remaining}")


def setup(bot):
    bot.add_cog(Gambling(bot))

