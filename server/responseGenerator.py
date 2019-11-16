from typing import List, Tuple


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
