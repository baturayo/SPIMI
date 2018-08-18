from src.Spimi import preprocess_docs, index_data
from src.Spimi.load_index_file import load_index
from src.Compress.GammaCode import GammaCode
from src.Compress.VariableByteCode import VariableByteCode
from time import time


def load_index_file(indexFileName):
    """
    Load prepared index file into memory to make a search
    :param indexFileName: name of index file
    :return: index file
    """
    return load_index('Index/%s' % indexFileName)


def search(query, btree, compression_type):
    """
    Search query terms in dictionary
    :param query: string object includes query
    :param btree: btree data structure to effectively find index file
    :param compression_type: string object indicates compression type 'Gamma' or 'VBencode"
    :return: found documents
    """
    found_docs = list()
    try:
        for query_term in query.split(' '):
            index_file_name = list(btree.keys(query_term))[0]
            index_file_dict = load_index_file(index_file_name)

            compressed_term_postings = index_file_dict[query_term]  # Find uncompressed posting list

            if compression_type == 'Gamma':
                gammaCode = GammaCode()
                uncompressed_term_postings = gammaCode.gamma_decode_block(compressed_term_postings.encode('hex'))  # Decompress posting
            elif compression_type == 'VBencode':
                uncompressed_term_postings = VariableByteCode.VB_decode(compressed_term_postings)  # Decompress posting

            else:
                raise Exception('Invalid compression type!')

            gap_decoded_postings = [sum(uncompressed_term_postings[0:i])
                                    for i in range(1, len(uncompressed_term_postings) + 1)]
            found_docs.append(gap_decoded_postings)

        # Sort list of lists based on length of the list for query optimisation
        found_docs = sorted(found_docs, key=len)
        # Find intersected docs
        intersected_docs = set.intersection(*map(set, found_docs))
        return intersected_docs

    except KeyError:
        # Query not found
        pass


def querying_docs():
    # Create index b-tree to find index files efficiently
    btree = index_data.create_index_btree()
    while True:
        query = raw_input("Type your query:")
        if index_data.get_doc_names('Blocks/')[0] == 'gamma_index.txt':
            compression_type = 'Gamma'
        elif index_data.get_doc_names('Blocks/')[0] == 'vb_index.txt':
            compression_type = 'VBencode'

        preprocessed_query = preprocess_docs.preprocess_doc(query)
        docs = search(preprocessed_query, btree, compression_type)
        try:
            print('Found document ids are: %s' % list(sorted(docs)))
        except TypeError:
            print('Not found')


def main():
    reindex = raw_input('Do you want to reindex the documents [y/n]?')
    if reindex == 'y':
        compression_type = raw_input('What posting compression technique do you want to use [Gamma/VBencode]? ')
        block_size = raw_input('Type the maximum block size in terms of bits for SPIMI algorithm: ')

        # Before indexing do preprocessing for all documents
        preprocess_docs.run(index_data.get_doc_names('Emails/Raw/'), 'Emails/Raw/', 'Emails/Preprocessed/')

        # Start indexing
        index_data.index_docs(compression_type, int(block_size))
        querying_docs()
    elif reindex == 'n':
        querying_docs()



if __name__ == '__main__':
    main()

