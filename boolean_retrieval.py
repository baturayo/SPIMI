import index_data
from load_index_file import load_index
from Compress.GammaCode import GammaCode
from Compress.VariableByteCode import VariableByteCode
from bitstring import BitArray


def build_index_gamma_code():
    """
    Build index file with gamma code
    """
    index_data.index_gamma_docs()


def load_index_file(postingCompressionType):
    """
    Load prepared index file into memory to make a search
    :param postingCompressionType: Gamma Code or VB encoding
    :return: index file
    """
    if postingCompressionType == 'Gamma':
        return load_index('Blocks/gamma_index.txt')
    elif postingCompressionType == 'VBencode':
        return load_index('Blocks/vb_code_index.txt')
    else:
        raise Exception('Invalid posting compression type! Use either "Gamma" or "VBencode!"')


def search(query, index_dict, compression_type):
    """
    Search query terms in dictionary
    :param query: string object includes query
    :param index_dict: dictionary object include index files
    :param compression_type: string object indicates compression type 'Gamma' or 'VBencode"
    :return: found documents
    """
    found_docs = list()
    for query_term in query.split(' '):
        compressed_term_postings = index_dict[query_term]  # Find uncompressed posting list
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

    print(found_docs)
    # Sort list of lists based on length of the list for query optimisation
    found_docs = sorted(found_docs,key=len)
    print (found_docs)
    # Find intersected docs
    intersected_docs = set.intersection(*map(set, found_docs))
    return intersected_docs


if __name__ == '__main__':
    compression_type = raw_input('Do you want to use Gamma or VBencode compression?')
    index_dict = load_index_file(compression_type)  # Load index file into a dictionary
    query = raw_input("Type your query:")
    docs = search(query, index_dict, compression_type)
    print(docs)

