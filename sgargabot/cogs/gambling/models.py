import mongoengine
import datetime

import sgargabot.utils.config as config

class SuperEnalottoEntry(mongoengine.Document):
    user_id = mongoengine.IntField(required=True)
    date_valid = mongoengine.DateTimeField(default=datetime.datetime.now(config.TZ_ZONEINFO))
    numbers = mongoengine.ListField(mongoengine.IntField(), required=True)

class SuperEnalottoPrize(mongoengine.Document):
    amount = mongoengine.IntField()
