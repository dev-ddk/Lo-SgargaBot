import discord
import datetime

from sgargabot.models.enums import EconomyTXNType


class InexistentCogError(Exception):
    def __init__(self, cog_name: str):
        super().__init__(f"Attempted reloading unexistant cog: {cog_name}")


class TooManyCallsError(Exception):
    def __init__(self, message, time_remaining: datetime.timedelta = datetime.timedelta(seconds=0)):
        super().__init__(message)
        self.time_remaining = time_remaining

    def get_remaining_time(self):
        # TODO: i18n
        if self.time_remaining.days:
            return f'{self.time_remaining.days} days' + (f' and {self.time_remaining.seconds // 3600} hours' if self.time_remaining.seconds // 3600 else '')
        elif self.time_remaining.seconds // 3600:
            minutes = (self.time_remaining.seconds % 3600) // 60
            return f'{self.time_remaining.seconds // 3600} hours' + (f' and {minutes} minutes' if minutes else '')
        elif self.time_remaining.seconds // 60:
            seconds = (self.time_remaining.seconds % 60)
            return f'{self.time_remaining.seconds // 60} minutes' + (f' and {seconds} seconds' if seconds else '')
        else:
            return f'{self.time_remaining.seconds} seconds'


class DBException(Exception):
    pass
