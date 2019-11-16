from sqlalchemy import create_engine, Column, Table, MetaData, Integer, String, ForeignKey, DateTime
from datetime import datetime
from hashlib import md5


class Record():
    def __init__(self, *args, **kwargs):
        if 'engine' in kwargs:
            self.engine = kwargs['engine']
        else:
            db_name = kwargs['db'] if 'db' in kwargs else 'db.sqlite3'
            self.engine = create_engine('sqlite:///{}'.format(db_name))

    def addTransaction(self, sender: str, foodId: int, amount: int) -> None:
        self.engine.execute(
            'INSERT INTO storeTransaction(sender, time, foodId, amount) VALUES (?,?,?,?)',
            (sender, datetime.now(), foodId, amount)
        )

    def addPresence(self, sender: str) -> None:
        self.engine.execute(
            'INSERT INTO presenceEmploree(sender, time) VALUES (?,?)', (sender, datetime.now())
        )

    def getAllTransactions(self):
        data = self.engine.execute('SELECT * FROM storeTransaction')
        return data.fetchall()

    def calculateAndCheckHash(self, file_data):
        md5_hasher = md5()
        md5_hasher.update(file_data)

        md5_hash = md5_hasher.hexdigest()

        result = self.engine.execute('SELECT * FROM imageHash WHERE hash = ?', (md5_hash, ))

        if len(result.fetchall()) >= 1:
            return False

        self.engine.execute('INSERT INTO imageHash(hash) VALUES (?)', (md5_hash, ))

        return True
