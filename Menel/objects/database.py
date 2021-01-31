from os import getenv

import motor.motor_asyncio


class Database:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            getenv('MONGODB_HOST'),
            tz_aware=False,
            connect=True,
            directConnection=False,
            appname='Menel',
            retryWrites=True,
            retryReads=True,
            compressors='zlib',
            zlibCompressionLevel=5,
            w=1,
            readPreference='primaryPreferred',
            tls=True
        )


database = Database()