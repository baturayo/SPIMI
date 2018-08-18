import compressed_spimi_gamma
import compressed_spimi_vbencode
from compressed_spimi_gamma import safe_readline, rename_file
from BTrees.OOBTree import OOBTree
from time import time
from os import listdir, rename, remove
import glob
import os
import re


def list_files(directory, extension):
    """
    List files of a specific extention type
    :param directory:
    :param extension:
    :return:
    """
    return [f for f in listdir(directory) if f.endswith('.' + extension)]


def get_doc_names(path):
    """
    Get data from Database
    :return: list of doc names
    """
    doc_names = list_files(path, 'txt')  # List of blocks

    # Sort doc names based on numbers
    doc_names.sort(key=lambda var: [int(x) if x.isdigit() else x for x in re.findall(r'[^0-9]|[0-9]+', var)])
    return doc_names


def define_doc_ids(doc_names):
    """
    This method change the name of the file and makes it a doc id
    E.g 'baturay.txt' -> '1.txt1' where 1 symbolises the doc id

    :param docs: list of document names
    :return: list of changed document names
    """
    # Check whether doc ids are defined if it is defined then there is an empty 000_flag.flg file
    path = 'Emails/Raw/'
    counter_id = 1
    if not os.path.exists(path + '000_flag.flg'):
        for name in doc_names:
            new_name = str(counter_id) + '.txt'
            rename(path + name, path + new_name)
            counter_id += 1

        temp = open(path + '000_flag.flg', 'w')
        temp.close()
    else:
        print('doc ids are already defined')


def delete_index_files(path):
    index_path = path
    files = glob.glob(index_path)
    for f in files:
        remove(f)


def split_merged_index():
    """
    This method split merged index files into 20 Kb chunks
    :return: index chunks file
    """
    index_path = 'Index/'
    merged_index_name = get_doc_names('Blocks/')[0]
    delete_index_files('Index/*')

    with open('Blocks/%s' % merged_index_name, 'rb') as merged_index:
        # Read first line of blocks
        current_line = merged_index.readline()
        dict_key = 'temp'
        chunkName = dict_key

        # Create a temp empty file before creating chunks
        tempFile = open(index_path + chunkName, 'wb')
        tempFile.close()

        while dict_key != '':
            if os.path.getsize(index_path + chunkName) < 20480:
                with open(index_path + chunkName, 'ab') as chunk:
                    dict_key, posting, next_line = safe_readline(merged_index, current_line)
                    chunk.write(current_line)
                    current_line = next_line

            else:
                # Rename file with the last dictionary key
                new_chunk_name = dict_key
                rename_file(index_path, chunkName, new_chunk_name)
                chunkName = 'temp'

                tempFile = open(index_path + chunkName, 'wb')
                tempFile.close()

        # Change the name of last chunk
        rename_file(index_path, 'temp', 'zzzzzzzzzzzzzzz')


def create_index_btree():
    """
    Build b-tree for efficient index file search
    """
    index_path = 'Index/'
    index_file_names = sorted(listdir(index_path))

    t = OOBTree()

    # Create a dictionary where there are file names on key and index on values
    name_id_dict = {k: v for v, k in enumerate(index_file_names)}
    t.update(name_id_dict)
    # Build tree
    return t


def index_docs(indexType, max_block_size):
    """
    Index documents
    :return:
    """
    original_doc_names = get_doc_names('Emails/Raw')
    define_doc_ids(original_doc_names)
    id_doc_names = get_doc_names('Emails/Raw')
    docs_path = 'Emails/Preprocessed/'

    # Delete all previously indexed files
    delete_index_files('Blocks/*')
    delete_index_files('Index/*')

    old_time = time()
    if indexType == 'Gamma':
        compressed_spimi_gamma.index_docs(id_doc_names, max_block_size, docs_path)
    elif indexType == 'VBencode':
        compressed_spimi_vbencode.index_docs(id_doc_names, max_block_size, docs_path)

    print('Index file is created in %s minutes!' % str((time() - old_time) / 60.0))
    split_merged_index()
