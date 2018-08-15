import sqlite3
import compressed_spimi_gamma
import compressed_spimi_vbencode
from time import time


def get_data():
    """
    Connect to database
    :return: cursor object to access to database
    """
    conn = sqlite3.connect(path)
    c = conn.cursor()
    data = c.execute('SELECT Id, RawText FROM Emails')
    return data


def index_docs(indexType, max_block_size):
    """
    Index documents
    :return:
    """
    docs = get_data()
    if indexType == 'Gamma':
        compressed_spimi_gamma.index_docs(docs, max_block_size)
    elif indexType == 'VBencode':
        compressed_spimi_vbencode.index_docs(docs, max_block_size)
    docs.close()


if __name__ == '__main__':
    path = 'Emails/database.sqlite'
    old_time = time()
    index_docs('Gamma', 100000)
    # print((time() - old_time) / 60.0)
    # # Define files
    # block1_file = open('temp.txt', 'rb')

    # # Read first
    # current_line = block1_file.readline()
    # while True:
    #
    #     dict_key, posting, next_line = compressed_spimi_gamma.safe_readline(block1_file, current_line)
    #     current_line = next_line
    #     if current_line == '':
    #         break
    # d1 = '.D1 10 Introduction. to data data data data data mining'
    # d2 = 'Data mining: concepts and techniques'
    # d3 = 'Elements of statistical learning'
    # d4 = 'Introduction to data mining'
    # d5 = 'Introduction to machine learning'
    #
    # blockCapacityLimit = 1000  # GLOBAL VAR
    # docs = [[1, d1], [2, d2], [3, d3], [4, d4], [5, d5]]
    # compressed_spimi_vbencode.index_docs(docs, blockCapacityLimit)





