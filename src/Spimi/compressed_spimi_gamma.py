"""
This script index documents by using SPIMI indexing technique
"""
from nltk.corpus import stopwords
from collections import defaultdict
from src.Compress.GammaCode import GammaCode
from bitstring import BitArray
from os import listdir
import sys
import os
import string
import re


def rename_file(path, old, new):
    """
    Rename a file
    """
    for f in os.listdir(path):
        os.rename(os.path.join(path, f),
                  os.path.join(path, f.replace(old, new)))


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

    # Remove numbers and stopwords
    if term in stopwords.words('english'):
        return ''

    escape_set = set(string.punctuation)  # Unwanted chars set
    # Remove the chars in the escape_set if it exists from the beginning and end of the term
    try:
        if term[0] in escape_set:
            term = ''.join(term[1:])

        if term[len(term) - 1] in escape_set:
            term = ''.join(term[:-1])

        # If there is a numeric value in term
        if not term.isalpha():
            return ''

        # Remove stopwords
        # if term not in stopwords.words('english'):
        #     # Stem terms
        #     ps = PorterStemmer()
        #     term = ps.stem(term)
        #     return term.lower()  # Convert to lower case and return
        # else:
        #     return ''  # Eliminate stop word
        return term.lower()
    except IndexError:
        return ''


def safe_readline(_file, curr_line):
    """
    At some lines x0a byte causes new lines and these bytes cause new line. Thus, the remaining posting lists passes
    to the line below. This method checks whether this is the case.
    Ex: x19\x20\xAB\x0a\x0b is represented as
    x19\x20\xAB\
    \x0b
    :param curr_line: string object defining current line
    :return:
    """
    def isCurrentSafe(txt):
        """
        This method checks whether the current line in a block is properly formatted. Safe means properly formatted.
        E.g pir,{i}\n is properly formatted because a string is followed by ,{ and after { there are bytes. Finally at
        the end there is }\n chars.

        :param txt: String object
        :return: True: properly formatted
                 False: otherwise
        """
        regex = '[a-zA-Z]+,{.*}\\n'
        if re.match(regex, txt) or txt == '':
            return True
        else:
            return False

    def isNextSafe(txt):
        """
        Check whether next line is safe to read.
        if it starts with char followed by ,{ then it is accepted to be safe
        E.g
        1-personally,{u}
        2-pm,{jk
        3-cds
        4-}
        In the example above the first line is considered to be current line and it is safe. The next line starts with
        pm,{ so it is also safe. For 2nd line this method will return true

        :param txt: string
        :return: True: properly formatted
                 False: otherwise
        """
        regex = '[a-zA-Z]+,{.*'
        if re.match(regex, txt) or txt == '':
            return True
        else:
            return False

    # Check if the current line is safe to proceed
    next_line = _file.readline()
    if curr_line == '' and next_line == '':
        return '', '', ''

    if isCurrentSafe(curr_line) and isNextSafe(next_line):
        _curr_dict, _curr_posting = curr_line.split(',', 1)

        return _curr_dict, _curr_posting[1:-2], next_line

    else:
        """
        There are some cases as the example below. Even if the first line is safe the second line is not because
        the posting list is 'csd}\nc' so we also need to check the next line even if the current line is safe.
        E.g: personal,{csd}\n
             c}
        """
        while True:
            if isNextSafe(next_line):
                _curr_dict, _curr_posting = curr_line.split(',', 1)
                return _curr_dict, _curr_posting[1:-2], next_line

            else:
                curr_line += next_line
                next_line = _file.readline()


def invert_block(docs, path):
    """
    The method creates a dictionary object of a fixed sized and try to add as much document as the capacity limit.
    The key of dict include the terms and the posting list have the document ids
    :param docs: List of string objects include multiple document
    :return: dictionary object
    """
    block_index = 0

    # Create dict block
    dictBlock = defaultdict(BitArray)
    gamma_code = GammaCode()


    # Iterate over docs
    for doc_name in docs:
        docID = int(doc_name.split('.')[0])
        with open(path + doc_name, 'r') as doc:
            doc = doc.read()
            doc = string.replace(doc, '\n', ' ')

            # TOKENIZE
            for term in doc.split(' '):
                term = preprocessDoc(term)
                # Check whether term has a char (if it is a stop word than term == '')
                if term != '':
                    # If term does not exist at keys before simply append doc ID
                    if dictBlock[term] == '':
                        gamma_code_encoded = gamma_code.gamma_encode_number(docID)
                        dictBlock[term].append(gamma_code_encoded)  # Append binary

                    # Else append the difference between last doc ID and current doc ID
                    else:
                        lastDocID = sum(gamma_code.gamma_decode(dictBlock[term]))
                        currentDocID = docID
                        diff = currentDocID - lastDocID
                        gamma_code_diff = gamma_code.gamma_encode_number(diff)  # Compress with gamma code
                        dictBlock[term].append(gamma_code_diff)  # Append binary

            if sys.getsizeof(dictBlock) > blockCapacityLimit:
                # Append dictBlock object to blocks list object
                saveBlockDict2Disc(block_index, dictBlock, 'wb', True)
                # Empty dict block
                dictBlock = defaultdict(BitArray)

                block_index += 1

    # Save dictBlock object to disc
    saveBlockDict2Disc(block_index, dictBlock, 'wb', True)


def saveBlockDict2Disc(blockIndex, block, format, isDict):
    """
    Save dictBlock object to disc
    :param blockIndex: name of block
    :param block: list or dict object that has collection of dictionaries
    :param format: string object that indicates the format of opening a file ('wb', 'r', 'w', 'a' etc)
    :return:
    """
    # Delete '' key from dict
    if isDict:
        try:
            del block['']
        except KeyError:
            pass

        # Sort dict block
        sortedDictBlock = list(sorted(block.items(), key=lambda t: t[0]))

    # Save dict block to disc
    fileName = 'Blocks/%s.txt' % blockIndex
    gammaCode = GammaCode()
    with open(fileName, format) as out:
        # If the block is dict object
        if isDict:
            for key, values in sortedDictBlock:
                compressed_pl = gammaCode.padding_before_saving_disc(values)
                try:
                    out.write(str(key) + ',{' + compressed_pl.tobytes() + '}\n')  # Write bytes into file
                except UnicodeEncodeError:
                    print(key)
        else: # If the block is list object
            for values in block:
                out.write(values)


def merge2CompressedPostingLists(posting1, posting2):
    """
    This method merge two compressed posting lists
    :param posting1: List Object
    :param posting2: List Object
    :return: merged posting list
    """
    gammaCode = GammaCode()
    decoded_posting1 = gammaCode.gamma_decode_block(posting1)
    decoded_posting2 = gammaCode.gamma_decode_block(posting2)
    first_element_posting2 = decoded_posting2[0]
    sum_posting1 = sum(decoded_posting1)
    mergedPosting = decoded_posting1 + [(first_element_posting2 - sum_posting1)] + decoded_posting2[1:]
    gamma_encoded_merged_posting = gammaCode.gamma_encode(mergedPosting)
    return gamma_encoded_merged_posting


def merging2Blocks(block1, block2):
    path = 'Blocks/'

    # Define files
    block1_file = open(path + block1, 'rb')
    block2_file = open(path + block2, 'rb')

    isComplete = False

    # Read first line of blocks
    current_line_1 = block1_file.readline()
    current_line_2 = block2_file.readline()
    dict_key_1, posting_1, next_line_1 = safe_readline(block1_file, current_line_1)
    dict_key_2, posting_2, next_line_2 = safe_readline(block2_file, current_line_2)
    current_line_1 = next_line_1
    current_line_2 = next_line_2

    # Define a Default Dict to store merged postings in memory
    cacheList = list()

    while not isComplete:
        # CASE 1: if keys are same
        if dict_key_1 == dict_key_2:
            block1_posting = posting_1.encode('hex')
            block2_posting = posting_2.encode('hex')

            merged_posting = merge2CompressedPostingLists(block1_posting, block2_posting)
            cacheList.append(dict_key_1 + ',{' + bytes(merged_posting.tobytes()) + '}\n')

            # Skip to Next  lines
            dict_key_1, posting_1, next_line_1 = safe_readline(block1_file, current_line_1)
            dict_key_2, posting_2, next_line_2 = safe_readline(block2_file, current_line_2)
            current_line_1 = next_line_1
            current_line_2 = next_line_2

        # CASE 2: if first block keys is greater than second key
        elif dict_key_1 > dict_key_2:
            cacheList.append(dict_key_2 + ',{' + posting_2 + '}\n')
            dict_key_2, posting_2, next_line_2 = safe_readline(block2_file, current_line_2)
            current_line_2 = next_line_2

        # CASE 3: if second block keys is greater than firs key
        elif dict_key_1 < dict_key_2:
            cacheList.append(dict_key_1 + ',{' + posting_1 + '}\n')
            dict_key_1, posting_1, next_line_1 = safe_readline(block1_file, current_line_1)
            current_line_1 = next_line_1

        # If first block is red completely append all the remaining rows from second block
        if dict_key_1 == '' and dict_key_2 != '':
            while not isComplete:
                cacheList.append(dict_key_2 + ',{' + posting_2 + '}\n')
                dict_key_2, posting_2, next_line_2 = safe_readline(block2_file, current_line_2)
                current_line_2 = next_line_2
                if dict_key_2 == '':
                    isComplete = True

        # If second block is red completely append all the remaining rows from first block
        if dict_key_1 != '' and dict_key_2 == '':
            while not isComplete:
                cacheList.append(dict_key_1 + ',{' + posting_1 + '}\n')
                dict_key_1, posting_1, next_line_1 = safe_readline(block1_file, current_line_1)
                current_line_1 = next_line_1
                if dict_key_1 == '':
                    isComplete = True

        if dict_key_1 == '' and dict_key_2 == '':
            isComplete = True

        # If memory is used greater than a value write dict to disc and flush the memory
        if sys.getsizeof(cacheList) > blockCapacityLimit:
            block_index = '_' + block1

            # Append dictBlock object to blocks list object
            saveBlockDict2Disc(block_index, cacheList, 'ab', False)

            # Empty list block / Flush Memory
            cacheList = list()

    block_index = '_' + block1
    # Append dictBlock object to blocks list object
    saveBlockDict2Disc(block_index, cacheList, 'ab', False)
    block1_file.close()
    block2_file.close()


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

        if n_blocks % 2 == 0:  # If number of blocks are even
            block_couples = [(i, i + 1) for i in range(0, n_blocks, 2)]
        else:
            block_couples = [(i, i + 1) for i in range(0, n_blocks - 1, 2)]

        for couple in block_couples:
            block1 = blockNames[couple[0]]
            block2 = blockNames[couple[1]]
            merging2Blocks(block1, block2)  # Merge two blocks
            deleteMergedBlocks(block1, block2)  # Delete blocks after merging

    blockNames, n_blocks = getSortedBlockNames()
    merged_index_file_name = blockNames[0]
    rename_file('Blocks/', merged_index_file_name, 'gamma_index.txt')


def index_docs(docs, buffer, path):
    """
    Main method that index the documents with SPIMI algorithm
    :param docs: Documents include doc ids and body text
    :param buffer_size: Maximum size of each block for SPIMI algorithm
    :param path: path of documents
    """
    print('--------------------------------------------')
    print('Indexing has been started..')
    global blockCapacityLimit
    blockCapacityLimit = buffer
    invert_block(docs, path)
    print('All documents are inverted!')
    mergeAllBlocks()
    print('All inverted blocks are merged!')
    print('--------------------------------------------')

# if __name__ == '__main__':
#     d1 = '.D1 10 Introduction. to data data data data data mining'
#     d2 = 'Data mining: concepts and techniques'
#     d3 = 'Elements of statistical learning'
#     d4 = 'Introduction to data mining'
#     d5 = 'Introduction to machine learning'
#
#     blockCapacityLimit = 1000  # GLOBAL VAR
#     docs = [d1, d2, d3, d4, d5]
#     invert_block(docs)
#     mergeAllBlocks()
#
#     with open('Blocks/gamma_index.txt', 'rb') as out:
#         gammaCode = GammaCode()
#         while True:
#             key, value = safe_readline(out)
#             value = value.encode('hex')
#             decompressed_value = gammaCode.gamma_decode_block(value)
#             print(key, decompressed_value)