import mongoengine
import datetime

class Call(mongoengine.EmbeddedDocument):
    # Names are fully qualified names such as CogName.command_name
    cmd = mongoengine.StringField()
    time_called = mongoengine.DateTimeField(default=datetime.datetime.utcnow)

class UserCalled(mongoengine.Document):
    user_id = mongoengine.IntField()
    cmds_called = mongoengine.EmbeddedDocumentListField(Call)

