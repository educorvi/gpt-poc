import datetime

from peewee import *

db = SqliteDatabase('/var/lib/gpt-poc/database.db')


class BaseModel(Model):
    class Meta:
        database = db


class Chat(BaseModel):
    cost = FloatField(default=0)
    tokens = IntegerField(default=0)
    start_time = DateTimeField(default=datetime.datetime.now)


db.connect()
db.create_tables([Chat])

