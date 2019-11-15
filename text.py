import sqlite3
import difflib
from typing import List, Tuple
from datetime import datetime

class textParser:
    def __init__(self, *args):
        if len(args) <= 1:
            db_name = args[0] if args else 'db.sqlite3'
            self.conn = sqlite3.connect(db_name)
            self.cursor = self.conn.cursor()

            try:
                self.cursor.execute('DROP TABLE foodType')
                self.cursor.execute('DROP TABLE keyword')
                self.cursor.execute('DROP TABLE transactions')

                self.conn.commit()
            except:
                pass
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
            self.cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS transactions(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                sender VARCHAR(20) NOT NULL,
                time timestamp NOT NULL,
                foodId INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                FOREIGN KEY(foodId) REFERENCES foodType(id) 
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

        elif len(args) == 2:
            self.conn = args[0]
            self.cursor = args[1]
        else:
            raise Exception('Invalid constructor')

    def __del__(self):
        self.conn.close()

    def getType(self) -> List[Tuple[int, str]]:
        data = self.cursor.execute('SELECT * FROM foodType')
        return data.fetchall()

    def addType(self, name: str) -> None:
        self.cursor.execute('INSERT INTO foodType(name) VALUES (?)', (name, ))
        self.conn.commit()

    def getTypeInfo(self, type_id: int) -> str:
        data = self.cursor.execute('SELECT name FROM foodType WHERE id = ?', (type_id, ))
        return data.fetchone()

    def getKeyword(self) -> List[Tuple[int, int, str]]:
        data = self.cursor.execute('SELECT * FROM keyword')
        return data.fetchall()

    def addKeyword(self, type_id: int, keyword: str) -> None:
        self.cursor.execute('INSERT INTO keyword(foodId, keyword) VALUES (?,?)', (type_id, keyword))
        self.conn.commit()

    def parseInput(self, text_input: str) -> Tuple[int, str, int]:
        number_in_text = [int(s) for s in text_input.split() if s.isdigit()]

        if len(number_in_text) == 0:
            raise Exception('No number in text')

        item_number = number_in_text[0]

        print('DEBUG: get {} item'.format(item_number))

        keyword_row = self.getKeyword()

        keyword_list = list(map(lambda x: x[2], keyword_row))
        food_id_list = list(map(lambda x: x[1], keyword_row))

        input_keyword = text_input[:text_input.index(str(item_number))]
        input_keyword = input_keyword.strip()

        matches = difflib.get_close_matches(input_keyword, keyword_list, 1)
        if len(matches) > 0:
            food_match_id = food_id_list[keyword_list.index(matches[0])]
            food_match_name = self.getTypeInfo(food_match_id)[0]

            print('DEBUG: match = {}'.format(food_match_name))

            return (food_match_id, food_match_name, item_number)
        else:
            print('DEBUG: no match')
            return (None, None, None)

    def addTransaction(self, sender: str, foodId: int, amount: int) -> None:
        self.cursor.execute('INSERT INTO transactions(sender, time, foodId, amount) VALUES (?,?,?,?)', (sender, datetime.now(), foodId, amount))
        self.conn.commit()

    def getAllTransactions(self):
        data = self.cursor.execute('SELECT * FROM transactions')
        return data.fetchall()


if __name__ == '__main__':
    parser = textParser()
    parser.addType('ayam geprek')
    parser.addType('ayam saos')

    parser.addKeyword(1, 'ayam geprek')
    parser.addKeyword(1, 'geprek')
    parser.addKeyword(1, 'ayam gprk')

    parser.addKeyword(2, 'ayam saos')
    parser.addKeyword(2, 'ayam bbq')
    parser.addKeyword(2, 'ayam blackpaper')
    parser.addKeyword(2, 'ayam blackpepper')

    parser.addTransaction('09238492',2,4)
    print(parser.getAllTransactions())

    # print(parser.parseInput('Ayam geprek 1'))
    # print(parser.parseInput('Ayam gprk 2'))
    # print(parser.parseInput('gprk 3'))
    # print(parser.parseInput('geprek 4'))

    # print(parser.parseInput('aym bbq 5'))
    # print(parser.parseInput('ayam blckpaper 6'))
