import discord
import mongoengine
import logging
import datetime
from functools import wraps, partial
from typing import Callable

import sgargabot.utils.config as config
from sgargabot.models.db import UserCalled, Call
from sgargabot.models.exceptions import TooManyCallsError, DBException

logger = logging.getLogger(__name__)


def callable_n_times(times: int):
    def _callable_n_times(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            user_id = args[1].author.id
            results = UserCalled.objects(cmds_called__cmd=f.__qualname__, user_id=user_id)
            len_results = len(results)
            if len_results > 1:
                # In theory this should never happen, but it's defensive programming
                raise DBException(f'Too many results for user {args[1].author.name} (ID: {args[1].author.id}) in collection user_called')
            elif len_results == 0:
                # There is no entry for the user (User has never issued cmds)
                call = Call(cmd=f.__qualname__)
                user_called = UserCalled(user_id=user_id, cmds_called=[call])
                user_called.save()
                return await f(*args, **kwargs)
            elif results.first().cmds_called.count() < times:
                # The number of previous calls still allows for one more call.
                # It's important that is strictly less than, since the current call should be included in the count
                call = Call(cmd=f.__qualname__)
                results.first().update(push__cmds_called=call)
                return await f(*args, **kwargs)
            else:
                raise TooManyCallsError(f'User {args[1].author.name} attempted to call the'
                                        f'command "{args[1].command}" more times than allowed (Command can '
                                        f'only be called {times} times). Command attempted: {args[1].message.content}.')
        return wrapper
    return _callable_n_times


def callable_once(f: Callable):
    return callable_n_times(1)(f)

def get_count_cmds_in_interval(cmds_called, cmd: str, from_time: datetime.datetime, to_time: datetime.datetime) -> int:
    #return cmds_called
    pass



def callable_n_times_within(times: int, interval: datetime.timedelta):
    """Decorator for wrapping functions that should be called at most `times` times within `interval`

    The decorator works in a sliding window fashion, counting the amount of calls in the
    interval of time of length `interval` before the current time.
    """
    def _callable_n_times_within(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            user_id = args[1].author.id
            date_to = datetime.datetime.utcnow()
            date_from = date_to - interval
            results = UserCalled.objects(cmds_called__cmd=f.__qualname__, user_id=user_id)
            len_results = len(results)
            if len_results > 1:
                # In theory this should never happen, but it's defensive programming
                raise DBException(f'Too many results for user {args[1].author.name} (ID: {args[1].author.id}) in collection user_called')
            elif len_results == 0:
                # There is no entry for the user (User has never issued cmds)
                call = Call(cmd=f.__qualname__)
                UserCalled(user_id=user_id, cmds_called=[call]).save()
                return await f(*args, **kwargs)
            elif results.first().cmds_called(
                mongoengine.Q(time_called__gte=date_from) &
                mongoengine.Q(time_called__lte=date_to)
            ).count() < times:
                # The number of previous calls still allows for one more call.
                # It's important that is strictly less than, since the current call should be included in the count
                results.first().cmds_called.create(cmd=f.__qualname__)
                return await f(*args, **kwargs)
            else:
                raise TooManyCallsError(f'User {args[1].author.name} attempted to call the'
                                        f'command "{args[1].command}" more times than allowed (Command can '
                                        f'only be called {times} times). Command attempted: {args[1].message.content}.')
        return wrapper
    return _callable_n_times_within
