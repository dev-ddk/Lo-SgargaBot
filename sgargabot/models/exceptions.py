import discord
import datetime

from sgargabot.models.enums import EconomyTXNType

class InexistentCogError(Exception):
    def __init__(self, cog_name: str):
        super().__init__(f'Attempted reloading unexistant cog: {cog_name}')

class TooManyCallsError(Exception):
    def __init__(self, *args, time_remaining: datetime.timedelta = 0, **kwargs):
        super().__init__(*args, **kwargs)
        self.time_remaining = time_remaining

class DBException(Exception):
    pass
