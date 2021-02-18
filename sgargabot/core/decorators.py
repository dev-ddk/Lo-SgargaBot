import discord
import mongoengine
import logging
import datetime
from zoneinfo import ZoneInfo
from functools import wraps, partial
from typing import Callable, Tuple

import sgargabot.utils.config as config
from sgargabot.models.db import UserCalled, to_field_name
from sgargabot.models.exceptions import TooManyCallsError, DBException

logger = logging.getLogger(__name__)


def callable_n_times(times: int):
    def _callable_n_times(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            user_id = args[1].author.id
            results = UserCalled.objects(user_id=user_id)
            len_results = len(results)
            if len_results > 1:
                # In theory this should never happen, but it's defensive programming
                raise DBException(
                    f"Too many results for user {args[1].author.name} (ID: {args[1].author.id}) in collection user_called"
                )
            elif len_results == 0:
                logger.debug("No previous entry")
                # There is no entry for the user (User has never issued cmds)
                res =  await f(*args, **kwargs)
                user_called = UserCalled(user_id=user_id)
                user_called.add_call(f.__qualname__)
                return res
            elif not hasattr(results.first(), to_field_name(f.__qualname__)):
                # User exists but has never called the command
                logger.debug("No previous command call")
                results.first().add_call(f.__qualname__)
            elif len(getattr(results.first(), to_field_name(f.__qualname__))) < times:
                # The number of previous calls still allows for one more call.
                # It's important that is strictly less than, since the current call should be included in the count
                res = await f(*args, **kwargs)
                logger.debug('aaaaaaa')
                results.first().add_call(f.__qualname__)
                return res
            else:
                raise TooManyCallsError(
                    f"User {args[1].author.name} attempted to call the"
                    f'command "{args[1].command}" more times than allowed (Command can '
                    f"only be called {times} times). Command attempted: {args[1].message.content}."
                )

        return wrapper

    return _callable_n_times


def callable_n_times_within(times: int, interval: datetime.timedelta):
    """Decorator for wrapping functions that should be called at most `times` times within `interval`

    The decorator works in a sliding window fashion, counting the amount of calls in the
    interval of time of length `interval` before the current time.
    """

    def _callable_n_times_within(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            user_id = args[1].author.id
            date_to = datetime.datetime.now(config.TZ_ZONEINFO)
            date_from = date_to - interval
            results = UserCalled.objects(user_id=user_id)
            len_results = results.count()
            field_name = to_field_name(f.__qualname__)
            if len_results > 1:
                # In theory this should never happen, but it's defensive programming
                raise DBException(
                    f"Too many results for user {args[1].author.name} (ID: {args[1].author.id}) in collection user_called"
                )
            elif len_results == 0:
                # There is no entry for the user (User has never issued cmds)
                res = await f(*args, **kwargs)
                user_called = UserCalled(user_id=user_id)
                user_called.add_call(f.__qualname__)
                return res
            elif not hasattr(results.first(), field_name):
                res = await f(*args, **kwargs)
                results.first().add_call(f.__qualname__)
                return res

            last_n_calls = _get_last_n_calls(times, field_name, results)

            if len(last_n_calls) < times:
                # Check if at least times called have been made: if not, then surely another call is possible
                res = await f(*args, **kwargs)
                results.first().add_call(f.__qualname__)
                return res
            elif last_n_calls[0] < date_from:
                # Check if the n-th most recent call allows for another call
                # It's important that is strictly less than, since the current call should be included in the count
                res = await f(*args, **kwargs)
                results.update_one(**{"pop__" + field_name: -1})
                results.first().add_call(f.__qualname__)
                return res
            else:
                time_remaining = interval - (date_to - last_n_calls[0])
                raise TooManyCallsError(
                    f"User {args[1].author.name} attempted to call the"
                    f'command "{args[1].command}" more times than allowed (Command can '
                    f"only be called {times} times). Command attempted: {args[1].message.content}.",
                    time_remaining=time_remaining,
                )

        return wrapper

    return _callable_n_times_within


def _get_last_n_calls(n, field_name: str, usercalled_objs: mongoengine.QuerySet):
    return getattr(
        usercalled_objs.fields(**{"slice__" + field_name: -1 * n}).first(), field_name
    )


def callable_once(f: Callable):
    return callable_n_times(1)(f)


def callable_once_within(interval: datetime.timedelta):
    return callable_n_times_within(1, interval)


def callable_every_24h(f: Callable):
    return callable_once_within(datetime.timedelta(hours=24))(f)


def callable_once_per_day(f: Callable):
    return callable_n_times_per_day(1)(f)


def callable_n_times_per_day(times: int):
    """Decorator for wrapping functions that should be called at most `times` times each day, with the counter resetting every midnight

    The decorator works in a sliding window fashion, counting the amount of calls in the
    current day.
    """

    def _callable_n_times_per_day(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            user_id = args[1].author.id
            date_to = datetime.datetime.now(config.TZ_ZONEINFO)
            results = UserCalled.objects(user_id=user_id)
            len_results = results.count()
            field_name = to_field_name(f.__qualname__)
            if len_results > 1:
                # In theory this should never happen, but it's defensive programming
                raise DBException(
                    f"Too many results for user {args[1].author.name} (ID: {args[1].author.id}) in collection user_called"
                )
            elif len_results == 0:
                # There is no entry for the user (User has never issued cmds)
                res = await f(*args, **kwargs)
                user_called = UserCalled(user_id=user_id)
                user_called.add_call(f.__qualname__)
                return res
            elif not hasattr(results.first(), field_name):
                res = await f(*args, **kwargs)
                results.first().add_call(f.__qualname__)
                return res

            last_n_calls = _get_last_n_calls(times, field_name, results)

            if len(last_n_calls) < times:
                # Check if at least times called have been made: if not, then surely another call is possible
                res = await f(*args, **kwargs)
                results.first().add_call(f.__qualname__)
                return res
            elif date_to - last_n_calls[0].replace(
                hour=0, minute=0, second=0, microsecond=0) > datetime.timedelta(hours=24):
                # Check if the n-th most recent call allows for another call
                # It's important that is strictly less than, since the current call should be included in the count
                res = await f(*args, **kwargs)
                results.update_one(**{"pop__" + field_name: -1})
                results.first().add_call(f.__qualname__)
                return res
            else:
                last_call = last_n_calls[0]
                next_day = last_call.replace(
                    hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
                time_remaining = next_day - date_to
                raise TooManyCallsError(
                    f"User {args[1].author.name} attempted to call the"
                    f'command "{args[1].command}" more times than allowed (Command can '
                    f"only be called {times} times). Command attempted: {args[1].message.content}.",
                    time_remaining=time_remaining,
                )

        return wrapper

    return _callable_n_times_per_day
