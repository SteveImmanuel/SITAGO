from sqlalchemy import create_engine, Table, Column, Integer, String, ForeignKey, MetaData, DateTime
import difflib
from typing import List, Tuple
from datetime import datetime
import re
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(levelname)s: %(message)s')


class textParser:
    def __init__(self, *args, **kwargs):
        if 'engine' in kwargs:
            self.engine = kwargs['engine']
        else:
            db_name = kwargs['db'] if 'db' in kwargs else 'db.sqlite3'
            self.engine = create_engine('sqlite:///{}'.format(db_name))

        metadata = MetaData()

        food_type = Table(
            'foodType',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String, nullable=False),
        )

        keyword = Table(
            'keyword',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('foodId', None, ForeignKey('foodType.id'), nullable=False),
            Column('keyword', String, nullable=False),
        )

        transaction = Table(
            'storeTransaction',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('sender', String(20), nullable=False),
            Column('time', DateTime, nullable=False),
            Column('foodId', None, ForeignKey('foodType.id'), nullable=False),
            Column('amount', Integer, nullable=False),
        )

        metadata.create_all(self.engine)

    def getType(self) -> List[Tuple[int, str]]:
        data = self.engine.execute('SELECT * FROM foodType')
        return data.fetchall()

    def addType(self, name: str) -> None:
        self.engine.execute('INSERT INTO foodType(name) VALUES (?)', (name, ))

    def getTypeInfo(self, type_id: int) -> str:
        data = self.engine.execute('SELECT name FROM foodType WHERE id = ?', (type_id, ))
        return data.fetchone()

    def getKeyword(self) -> List[Tuple[int, int, str]]:
        data = self.engine.execute('SELECT * FROM keyword')
        return data.fetchall()

    def addKeyword(self, type_id: int, keyword: str) -> None:
        self.engine.execute('INSERT INTO keyword(foodId, keyword) VALUES (?,?)', (type_id, keyword))

    def addTransaction(self, sender: str, foodId: int, amount: int) -> None:
        self.engine.execute(
            'INSERT INTO storeTransaction(sender, time, foodId, amount) VALUES (?,?,?,?)',
            (sender, datetime.now(), foodId, amount)
        )

    def getAllTransactions(self):
        data = self.engine.execute('SELECT * FROM storeTransaction')
        return data.fetchall()

    def parseInput(self, text_input: str) -> Tuple[int, str, int]:
        logger = logging.getLogger()

        transactions = re.split(',|\n', text_input)
        transactions = [i.strip() for i in transactions]
        result = []
        for transaction in transactions:
            number_in_text = [int(s) for s in transaction.split() if s.isdigit()]

            if len(number_in_text) == 0:
                raise Exception('No number in text')

            item_number = number_in_text[0]

            logger.debug("Get {} item".format(item_number))

            keyword_row = self.getKeyword()

            keyword_list = list(map(lambda x: x[2], keyword_row))
            food_id_list = list(map(lambda x: x[1], keyword_row))

            input_keyword = transaction[:transaction.index(str(item_number))]
            input_keyword = input_keyword.strip()

            matches = difflib.get_close_matches(input_keyword, keyword_list, 1)
            if len(matches) > 0:
                food_match_id = food_id_list[keyword_list.index(matches[0])]
                food_match_name = self.getTypeInfo(food_match_id)[0]

                logger.debug('Match = {}'.format(food_match_name))
                result.append((food_match_id, food_match_name, item_number))
            else:
                logger.debug('No match')
                raise Exception('No matches')
        return result


class responseGenerator():
    first_column_length = 14
    second_column_length = 5

    @staticmethod
    def getHorizontalBorder() -> str:
        first_column = '-' * responseGenerator.first_column_length
        second_column = '-' * responseGenerator.second_column_length
        return ('+' + first_column + '+' + second_column + '+')

    @staticmethod
    def generateTransactionTable(transaction_list: List[Tuple[int, str, int]]) -> str:
        #list of tuple (foodId, foodName, amount)
        response = [responseGenerator.getHorizontalBorder()]
        for item in transaction_list:
            item_row = ['| ']
            item_row.append(item[1])  # foodName
            item_row.append(' ' * (responseGenerator.first_column_length - len(item[1]) - 1))
            item_row.append('| ')
            item_row.append(str(item[2]))  # amount
            item_row.append(' ' * (responseGenerator.second_column_length - len(str(item[2])) - 1))
            item_row.append('|')
            response.append(''.join(item_row))
        response.append(responseGenerator.getHorizontalBorder())

        return '```{}```'.format('\n'.join(response))


if __name__ == '__main__':
    parser = textParser(db='db_test.sqlite3')
    parser.addType('ayam geprek')
    parser.addType('ayam saos')

    parser.addKeyword(1, 'ayam geprek')
    parser.addKeyword(1, 'geprek')
    parser.addKeyword(1, 'ayam gprk')

    parser.addKeyword(2, 'ayam saos')
    parser.addKeyword(2, 'ayam bbq')
    parser.addKeyword(2, 'ayam blackpaper')
    parser.addKeyword(2, 'ayam blackpepper')

    parser.addTransaction('09238492', 1, 4)

    # a = [('Ayam Geprek', 5)]
    # print(ResponseGenerator.generateTransactionTable(a))

    print(parser.parseInput('Ayam geprek 1'))
    print(parser.parseInput('Ayam gprk 2'))
    print(parser.parseInput('gprk 3'))
    print(parser.parseInput('geprek 4'))

    print(parser.parseInput('aym bbq 5'))
    print(parser.parseInput('ayam blckpaper 6'))
