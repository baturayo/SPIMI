"""
This script index documents by using SPIMI indexing technique
"""
import string
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from collections import defaultdict
from os import listdir
import sys
import os


def getSortedBlockNames():
    """
    Find block names from a dir and sort them based on block id
    :return: Sorted block names and number of blocks
    """
    def list_files(directory, extension):
        return (f for f in listdir(directory) if f.endswith('.' + extension))

    blockNames = list_files('Blocks/', 'txt')  # List of blocks
    blockNames_pos = [(int(filter(str.isdigit, blockName)), blockName) for blockName in blockNames]  # (Block id, names)
    sorted_blockID_Names = sorted(blockNames_pos, key=lambda x: x[0])  # Sort based on block id
    blockNames = [name for id, name in sorted_blockID_Names]  # Grab only block name from (block id, name) tuple
    n_blocks = len(blockNames)  # Number of blocks
    return blockNames, n_blocks


def preprocessDoc(term):
    """
    Stopword elimination, converting lower case, stemming, punctuation removal are done in this step
    :param doc: string object (term)
    :return:  preprocessed string object
    """

    # Convert Lowercase
    term = term.lower()

    # Remove punctuation marks from the beginning and end of the term
    if term[0] in set(string.punctuation):
        term = ''.join(term[1:])

    if term[len(term) - 1] in set(string.punctuation):
        term = ''.join(term[:-1])

    # Remove numbers
    if term.isdigit():
        term = ''

    # Remove stopwords
    if term not in stopwords.words('english'):
        # # Stem terms
        ps = PorterStemmer()
        term = ps.stem(term)
        return term
    else:
        return ''  # Eliminate stop word


def invert_block(docs, blockCapacityLimit=1000):
    """
    The method creates a dictionary object of a fixed sized and try to add as much document as the capacity limit.
    The key of dict include the terms and the posting list have the document ids
    :param blockCapacityLimit: Size limit of dictBlock dictionary object in terms of bytes
    :param docs: List of string objects include multiple document
    :return: dictionary object
    """
    block_index = 0
    i = 0
    prev_i = 0  # use for posting list compression
    # Create dict block
    dictBlock = defaultdict(list)

    # Iterate over docs
    for doc in docs:
        terms_in_doc = dict()
        # TOKENIZE
        for term in doc.split(' '):
            term = preprocessDoc(term)
            # Check whether term has a char (if it is a stop word than term == '')
            if term != '' and not terms_in_doc.has_key(term):
                # If term does not exist at keys before simply append doc ID
                dictBlock[term].append(i)

        if sys.getsizeof(dictBlock) > blockCapacityLimit:
            # Append dictBlock object to blocks list object
            saveBlockDict2Disc(block_index, dictBlock)
            # Empty dict block
            dictBlock = defaultdict(list)

            block_index += 1
        i += 1

    # Save dictBlock object to disc
    saveBlockDict2Disc(block_index, dictBlock)


def saveBlockDict2Disc(blockIndex, dictBlock):
    """
    Save dictBlock object to disc
    :param blocks: fixed sized dictionary object
    :param dictBlock: list object that has collection of dictionaries
    :return: empty dictBlock object
    """
    # Delete '' key from dict
    try:
        del dictBlock['']
    except KeyError:
        pass

    # Sort dict block
    sortedDictBlock = list(sorted(dictBlock.items(), key=lambda t: t[0]))

    # Save dict block to disc
    fileName = 'Blocks/%s.txt' % blockIndex
    with open(fileName, 'w') as out:
        for key, values in sortedDictBlock:
            out.write(str(key) + ',' + str(values)[1:-1].replace(' ', '') + '\n')


def merging2Blocks(block1, block2):
    isComplete = False
    path = 'Blocks/'

    # Define files
    block1_file = open(path + block1, 'rt')
    block2_file = open(path + block2, 'rt')

    # Read first lines
    block1_line = block1_file.readline()[:-1].split(',')  # Delete \n
    block2_line = block2_file.readline()[:-1].split(',')  # Delete \n

    while not isComplete:
        # CASE 1: if keys are same
        if block1_line[0] == block2_line[0]:
            with open(path + '_' + block1, 'a') as out:
                block1_posting = [int(val) for val in block1_line[1:]]
                block2_posting = [int(val) for val in block2_line[1:]]
                merged_posting = block1_posting + block2_posting

                out.write(block1_line[0] + ',' + str(merged_posting)[1:-1].replace(' ', '') + '\n')
            # Skip to Next  lines
            block1_line = block1_file.readline()[:-1].split(',')
            block2_line = block2_file.readline()[:-1].split(',')

        # CASE 2: if first block keys is greater than second key
        elif block1_line[0] > block2_line[0]:
            with open(path + '_' + block1, 'a') as out:
                block2_posting = [int(val) for val in block2_line[1:]]

                out.write(block2_line[0] + ',' + str(block2_posting)[1:-1] + '\n')
            block2_line = block2_file.readline()[:-1].split(',')

        # CASE 3: if second block keys is greater than firs key
        elif block1_line[0] < block2_line[0]:
            with open(path + '_' + block1, 'a') as out:
                block1_posting = [int(val) for val in block1_line[1:]]

                out.write(block1_line[0] + ',' + str(block1_posting)[1:-1] + '\n')
            # Skip to Next  lines
            block1_line = block1_file.readline()[:-1].split(',')

        # If first block is red completely append all the remaining rows from second block
        if block1_line[0] == '' and block2_line[0] != '':
            while not isComplete:
                with open(path + '_' + block1, 'a') as out:
                    block2_posting = [int(val) for val in block2_line[1:]]
                    out.write(block2_line[0] + ',' + str(block2_posting)[1:-1] + '\n')
                block2_line = block2_file.readline()[:-1].split(',')
                if block2_line[0] == '':
                    isComplete = True

        # If second block is red completely append all the remaining rows from first block
        if block1_line[0] != '' and block2_line[0] == '':
            while not isComplete:
                with open(path + '_' + block1, 'a') as out:
                    block1_posting = [int(val) for val in block1_line[1:]]
                    out.write(block1_line[0] + ',' + str(block1_posting)[1:-1] + '\n')
                block1_line = block1_file.readline()[:-1].split(',')
                if block1_line[0] == '':
                    isComplete = True

        if block1_line[0] == '' and block2_line[0] == '':
            isComplete = True


def deleteMergedBlocks(block1, block2):
    """
    Delete merged blocks from disc
    :param block1:
    :param block2:
    :return:
    """
    path = 'Blocks/'
    os.remove(path + block1)
    os.remove(path + block2)


def mergeAllBlocks():
    blockNames, n_blocks = getSortedBlockNames()

    # Merge blocks until there are one big merged block left
    while n_blocks > 1:
        blockNames, n_blocks = getSortedBlockNames()

        if n_blocks % 2 == 0: # If number of blocks are even
            block_couples = [(i, i + 1) for i in range(0, n_blocks, 2)]
        else:
            block_couples = [(i, i + 1) for i in range(0, n_blocks - 1, 2)]

        for couple in block_couples:
            block1 = blockNames[couple[0]]
            block2 = blockNames[couple[1]]
            merging2Blocks(block1, block2)  # Merge two blocks
            deleteMergedBlocks(block1, block2)  # Delete blocks after merging

if __name__ == '__main__':
    d1 = '.D1 Introduction. to data mining'
    d2 = 'Data mining: concepts and techniques'
    d3 = 'Elements of statistical learning'
    d4 = 'Introduction to data mining'
    d5 = 'Introduction to machine learning'
    docs = [d1, d2, d3, d4, d5, d1, d2, d3, d4, d5, d3, d4, d5, d3, d4, d5, d3, d4, d1]
    invert_block(docs)
    mergeAllBlocks()
