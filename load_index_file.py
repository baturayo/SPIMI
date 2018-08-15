"""
Load index files into memory in a dictionary
"""
from compressed_spimi_gamma import safe_readline


def load_index(index_path):
    index_dict = dict()
    with open(index_path) as index_file:
        first_line = index_file.readline()
        dict_key, posting, next_line = safe_readline(index_file, first_line)
        current_line = next_line

        # Iterate over all rows in index file
        while True:
            # Get posting list and dictionary key
            dict_key, posting, next_line = safe_readline(index_file, current_line)
            current_line = next_line

            # If the iteration reach the end of the index file than break the loop
            if dict_key == '' and posting == '':
                break

            # Insert key and postings to dictionary to make a fast search
            index_dict[dict_key] = posting

    return index_dict


