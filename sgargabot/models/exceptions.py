import discord

from sgargabot.models.enums import EconomyTXNType

class InexistentCogError(Exception):
    def __init__(self, cog_name: str):
        super().__init__(f'Attempted reloading unexistant cog: {cog_name}')

class TooManyCallsError(Exception):
    pass

class DBException(Exception):
    pass
