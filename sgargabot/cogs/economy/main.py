import logging
import discord
import mongoengine

from discord.ext import commands
from sgargabot.core.decorators import callable_once_per_day
from sgargabot.models.exceptions import TooManyCallsError
from sgargabot.utils.config import BotConfig
from .models import Wallet, TXN

logger = logging.getLogger(__name__)

# TODO: Replace the MongoDB economy backend with the correct backend

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="wallet")
    async def wallet(self, ctx):
        wallet = Wallet.objects(user_id=ctx.author.id)
        if wallet.count() == 0:
            await ctx.send('Please register a new economy account')
        elif wallet.count() == 1:
            await ctx.send(f'Your balance: {wallet.first().amount}')
        else:
            logger.error('Found two wallets with the same ID!')
            await ctx.send(f'Something wrong occurred!')


    @commands.command(name="daily")
    @callable_once_per_day
    async def daily(self, ctx):
        wallet = Wallet.objects(user_id=ctx.author.id)
        amount = BotConfig().DAILY_AMOUNT
        if wallet.count() == 0:
            await ctx.send('Please register a new economy account')
        elif wallet.count() == 1:
            wallet.update_one(inc__amount=amount)
            await ctx.send(f'You just earned your daily {amount} goleadoro!')
        else:
            logger.error('Found two wallets with the same ID!')
            await ctx.send(f'Something wrong occurred!')

    @daily.error
    async def daily_error(self, ctx, error):
        logger.info(error)
        if isinstance(error.original, TooManyCallsError):
            await ctx.send(f'You already received your daily amount! Time before your next possible daily reward: {error.original.get_remaining_time()}')

    @commands.command(name="transfer")
    async def transfer(self, ctx, member: discord.Member, amount: int):
        sender = Wallet.objects(user_id=ctx.author.id)
        recipient = Wallet.objects(user_id=member.id)
        logger.info(amount)
        if sender.count() == 0:
            await ctx.send('Please register a new economy account')
        elif recipient.count() == 0:
            await ctx.send("The chosen recipient doesn't have an economy account")
        elif amount <= 0:
            await ctx.send("Please provide a positive amount of goleadoro to transfer")
        elif ctx.author.id == member.id:
            await ctx.send("You cannot send money to yourself")
        elif sender.count() == 1 and recipient.count() == 1:
            if sender.first().amount < amount:
                await ctx.send("Not enough funds to complete the transaction")
            elif TXN.objects(sender=ctx.author.id, confirmed=False, cancelled=False).count() > 1:
                await ctx.send(f"You have a pending transaction. Please confirm or cancel it before attempting new transactions")
            else:
                # Congrats to MongoDB for not offering atomic transactions without a sharded DB smh
                txn = TXN(sender=ctx.author.id, recipient=member.id, amount=amount)
                txn.save()
                await ctx.send(f"You're attempting a transaction between you ({ctx.author.mention}) and {member.mention}. To confirm, execute $confirm. To cancel, execute $cancel")
        else:
            logger.error('Found two wallets with the same ID!')
            await ctx.send(f'Something wrong occurred!')

    @transfer.error
    async def transfer_error(self, ctx, error):
        if isinstance(error, commands.errors.MemberNotFound):
            await ctx.send('The recipient was not found')
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send('Command is incomplete')
        elif isinstance(error, commands.errors.BadArgument):
            await ctx.send('The transfer amount is not an integer')


    @commands.command(name="confirm")
    async def confirm(self, ctx):
        txns = TXN.objects(sender=ctx.author.id, confirmed=False, cancelled=False)
        if txns.count() > 1:
            logger.error(f'Too many pending transactions for user {ctx.author.id}')
            await ctx.send(f'Something wrong occurred!')
        elif txns.count() == 0:
            await ctx.send('No currently pending transactions')
        else:
            logger.info(txns.first())
            amount = txns.first().amount
            recipient_id = txns.first().recipient
            sender = Wallet.objects(user_id=ctx.author.id)
            recipient = Wallet.objects(user_id=txns.first().recipient)
            if sender.first().amount < amount:
                txns.update_one(set__cancelled=True)
                await ctx.send("Not enough funds to complete the transaction")
            else:
                txns.update_one(set__confirmed=True)
                sender.update_one(dec__amount=amount)
                recipient.update_one(inc__amount=amount)
                await ctx.send(f"Transaction between {ctx.author.mention} and <@{recipient_id}> completed")

    @commands.command(name="cancel")
    async def cancel(self, ctx):
        txns = TXN.objects(sender=ctx.author.id, confirmed=False, cancelled=False)
        if txns.count() > 1:
            logger.error(f'Too many pending transactions for user {ctx.author.id}')
            await ctx.send(f'Something wrong occurred!')
        elif txns.count() == 0:
            await ctx.send('No currently pending transactions')
        else:
            recipient_id = txns.first().recipient
            txns.update_one(set__cancelled=True)
            await ctx.send(f"Transaction between {ctx.author.mention} and <@{recipient_id}> cancelled")


    @commands.command(name="register")
    async def register(self, ctx):
        if Wallet.objects(user_id=ctx.author.id).count() != 0:
            await ctx.send("You've already registered!")
        else:
            wallet = Wallet(user_id=ctx.author.id, amount=0)
            wallet.save()
            await ctx.send("Wallet created!")

def setup(bot):
    bot.add_cog(Economy(bot))
