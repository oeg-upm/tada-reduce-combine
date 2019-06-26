from peewee import SqliteDatabase, Model, CharField, IntegerField, ForeignKeyField, BooleanField

DATABASE = 'data.db'
#DATABASE = ":memory:"

# database = SqliteDatabase(DATABASE)

local_database = SqliteDatabase(DATABASE)

def get_database(database=None):
    if database is None:
        database = DATABASE

    return local_database
    # return SqliteDatabase(database, pragmas=[('journal_mode', 'wal')])
    #return SqliteDatabase(database)



class BaseModel(Model):
    class Meta:
        database = get_database()


STATUS_NEW, STATUS_PROCESSING, STATUS_COMPLETE, STATUS_STOPPED = "New", "Processing", "Complete", "Stopped"
APPLE_STATUSES = [
    STATUS_NEW, STATUS_PROCESSING, STATUS_COMPLETE, STATUS_STOPPED
]


class Apple(BaseModel):
    table = CharField()  # table name or id
    column = IntegerField()  # column order (position)
    total = IntegerField()  # Total number of bites/slices
    status = CharField(default=STATUS_NEW, choices=APPLE_STATUSES)  # the status of merging
    complete = BooleanField(default=False)  # Whether there are missing slices or not
    fname = CharField(default="")


class Bite(BaseModel):
    slice = IntegerField()  # slice order (position)
    apple = ForeignKeyField(Apple, backref='bites')
    m = IntegerField()  # the number of cells that has at least one entity
    fname = CharField(null=True)  # the name of the file


def create_tables():
    print("creating tables ...\n\n")
    database = get_database()
    with database:
        database.create_tables([Apple, Bite, ], safe=True)
    # database.connect(reuse_if_open=True)
    # database.create_tables([Apple, Bite, ])


