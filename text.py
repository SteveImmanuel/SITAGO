import sqlite3
from typing import List, Tuple


class textParser:
    def __init__(self, db_name: str = 'db.sqlite3'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

        # Init table
        self.cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS foodType(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            name VARCHAR(60) NOT NULL
        );"""
        )
        self.cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS keyword(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            foodId INTEGER NOT NULL,
            keyword VARCHAR(60) NOT NULL,
            FOREIGN KEY(foodId) REFERENCES foodType(id) 
        );"""
        )
        self.conn.commit()

    def __del__(self):
        self.conn.close()

    def getType(self) -> List[Tuple[int, str]]:
        data = self.cursor.execute('SELECT * FROM foodType')
        return data.fetchall()

    def addType(self, name: str) -> None:
        self.cursor.execute('INSERT INTO foodType(name) VALUES (?)', (name, ))
        self.conn.commit()

    def getKeyword(self) -> List[Tuple[int, int, str]]:
        data = self.cursor.execute('SELECT * FROM keyword')
        return data.fetchall()

    def addKeyword(self, type_id: int, keyword: str) -> None:
        self.cursor.execute('INSERT INTO keyword(foodId, keyword) VALUES (?,?)', (type_id, keyword))
        self.conn.commit()

    def parseInput(self, text_input: str) -> None:
        pass


if __name__ == '__main__':
    parser = textParser()
    parser.addType('ayam geprek')
    parser.addType('ayam saos')

    parser.addKeyword(1, 'ayam geprek')

    print(parser.getKeyword())

    print(parser.getType())