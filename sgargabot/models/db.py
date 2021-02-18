import mongoengine
import datetime

import sgargabot.utils.config as config


class UserCalled(mongoengine.DynamicDocument):
    user_id = mongoengine.IntField()

    def add_call(self, cmd):
        cmd = to_field_name(cmd)
        if not hasattr(self, cmd):
            self.__setattr__(cmd, [datetime.datetime.now(config.TZ_ZONEINFO)])
        else:
            getattr(self, cmd).append(datetime.datetime.now(config.TZ_ZONEINFO))
        self.save()


def to_field_name(cmd):
    return cmd.replace(".", "_")
