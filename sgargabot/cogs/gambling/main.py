import logging
import discord
import datetime
import random
import asyncio

from discord.ext import commands
from .models import SuperEnalottoEntry, SuperEnalottoPrize
from sgargabot.cogs.economy.models import Wallet #This is temporary, until we create the unified economy backend
from async_cron.job import CronJob

import sgargabot.utils.config as config

logger = logging.getLogger(__name__)

random.seed(None)

class Gambling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        job = CronJob(name='superenalotto_extract').every().day.at('00:00').go(self.extract_superenalotto)
        #job = CronJob(name='superenalotto_extract').every(30).second.go(self.extract_superenalotto)
        self.bot.scheduler.add_job(job)

    @commands.command(name="superenalotto")
    async def superenalotto(self, ctx, numbers: commands.Greedy[int]):
        if len(numbers) != 6:
            await ctx.send("You must send a space-separated list of 6 integers")
        else:
            if len(set(numbers)) != 6:
                await ctx.send("All numbers must be different")
                return
            for num in numbers:
                if num not in range(1, 91):
                    await ctx.send("All numbers in the list must be between 1 and 91")
                    return
            wallet = Wallet.objects(user_id=ctx.author.id)
            cfg = config.BotConfig()
            if wallet.count() > 1:
                logger.error('Found two wallets with the same ID!')
                await ctx.send(f'Something wrong occurred!')
            elif wallet.count() == 0:
                await ctx.send('Please register a new economy account')
            elif wallet.first().amount < cfg.SUPERENALOTTO_TICKET_PRICE:
                await ctx.send("You don't have enough money for a ticket")
            else:
                wallet.update_one(dec__amount=cfg.SUPERENALOTTO_TICKET_PRICE)
                entry = SuperEnalottoEntry(user_id=ctx.author.id, numbers=numbers)
                entry.save()
                await ctx.send("Your bet has been registered. The extraction will happen at midnight. Good luck!")


    async def extract_superenalotto(self):
        cfg = config.BotConfig()
        channels = [self.bot.get_channel(ch) for ch in cfg.SUPERENALOTTO_CHANNELS]
        channels = [ch for ch in channels if ch]
        prize = None

        if not channels:
            return

        await broadcast_msg(channels, f'Superenalotto extraction of today ({datetime.datetime.now(config.TZ_ZONEINFO).strftime("%d/%m/%y")})')

        if SuperEnalottoPrize.objects().count() > 1:
            logger.error('There is more than one instance of the prize!')
            return
        elif SuperEnalottoPrize.objects().count() == 0:
            prize = SuperEnalottoPrize(amount=cfg.SUPERENALOTTO_INIT_PRIZE)
            prize.save()

        prize = prize or SuperEnalottoPrize.objects.first()

        if SuperEnalottoEntry.objects.count() == 0:
            await broadcast_msg(channels, f'Today nobody played SuperEnalotto, so I will keep all the money :)')
            return

        await broadcast_msg(channels, f'The total prize pool for today is {prize.amount} goleadoro!')

        extraction = set(random.sample(range(1, 91), 6))
        for num in extraction:
            await asyncio.sleep(1)
            await broadcast_msg(channels, f'Extracted the number: {num}')

        winnings = {i: [] for i in range(2, 7)}

        winning_amount = 0

        for entry in SuperEnalottoEntry.objects:
            intersect = extraction & set(entry.numbers)
            if len(intersect) in range(2, 7):
                await broadcast_msg(channels, f'Congratulations! <@{entry.user_id}> got {len(intersect)} numbers right! (Their entry was {", ".join(map(str, entry.numbers))})')
                winnings[len(intersect)].append(entry.user_id)

        for correct, user_list in winnings.items():
            if len(user_list) != 0:
                mentions = ', '.join(map(user_id_to_mention, user_list))
                split = cfg.SUPERENALOTTO_SPLIT[str(correct)]
                win_each = split * prize.amount // (100 * len(user_list))
                await broadcast_msg(channels, f'The following users have guessed {correct} numbers and will share {split}% of the prize pool: {mentions}. They win {win_each} goleadoro each!')
                for user in user_list:
                    Wallet.objects(user_id=user).update_one(inc__amount=win_each)
                    winning_amount += win_each

        SuperEnalottoPrize.objects.update_one(inc__amount=(SuperEnalottoEntry.objects.count() * cfg.SUPERENALOTTO_TICKET_PRICE - winning_amount + 100))
        SuperEnalottoEntry.objects.delete()

        await broadcast_msg(channels, f'See you next time!')


async def broadcast_msg(channels: list, msg: str):
    tasks = [ch.send(msg) for ch in channels]
    await asyncio.gather(*tasks)

def user_id_to_mention(user_id: int):
    return f'<@{user_id}>'


def setup(bot):
    bot.add_cog(Gambling(bot))
