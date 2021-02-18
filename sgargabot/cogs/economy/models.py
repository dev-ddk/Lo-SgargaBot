import mongoengine

class Wallet(mongoengine.Document):
    user_id = mongoengine.IntField(required=True)
    amount = mongoengine.IntField(required=True)

class TXN(mongoengine.Document):
    sender = mongoengine.IntField(required=True)
    recipient = mongoengine.IntField(required=True)
    amount = mongoengine.IntField(required=True)
    confirmed = mongoengine.BooleanField(default=False)
    cancelled = mongoengine.BooleanField(default=False)
