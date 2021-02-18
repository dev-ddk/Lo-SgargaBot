import discord
from typing import Tuple
from sgargabot.models.enums import EconomyTXNType


def check_balance(member: discord.Member) -> int:
    # TODO: connect to economy database
    return 100


def pay(from_user: discord.Member, to_user: discord.Member) -> None:
    # TODO: connect to economy database
    pass


def increase_balance(member: discord.Member, amount: int) -> None:
    # TODO: connect to economy database
    pass


def decrease_balance(member: discord.Member, amount: int) -> None:
    # TODO: connect to economy database
    pass
