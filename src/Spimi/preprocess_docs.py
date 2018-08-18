"""
Pre-process docs in a dataset such as stop word elimination, converting lower case, stemming, punctuation
removal
"""
import string
import index_data
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from time import time
import os


def remove_stopword(term):
    """
    Remove stop words
    :param doc: string object (term)
    :return:    preprocessed string object
    """
    if term in stopwords.words('english'):
        term = ''
    return term


def remove_number(term):
    """
    Remove number
    :param term: string object (term)
    :return: number free term
    """
    if not term.isalpha():
        return ''
    return term


def remove_punctuations(term):
    """
    Remove punctuations
    :param term: string object (term)
    :return: punctuation free terms
    """
    try:
        term = str(term)
        translator = string.maketrans(string.punctuation, ' ' * len(string.punctuation))  # map punctuation to space
        term = term.translate(translator)
        return term

    except UnicodeEncodeError:
        return ''


def convert_lowercase(term):
    """
    Remove punctuations
    :param term: string object (term)
    :return: punctuation free terms
    """
    return term.lower()


def stem_term(term):
    """
    Apply stemming
    :param term: string object (term)
    :return: stemmed term
    """
    if term not in stopwords.words('english'):
        # Stem terms
        ps = PorterStemmer()
        term = ps.stem(term)
        return term  # Convert to lower case and return
    else:
        return ''  # Eliminate stop word


def unfiltered_stats_0(verbose=False):
    path = 'Emails/Raw/'
    docs = index_data.get_doc_names(path)
    term_set = set()

    # Unfiltered
    for doc_name in docs:
        with open(path + doc_name, 'r') as _doc:
            doc = _doc.read()
            doc = string.replace(doc, '\n', ' ')
            for term in doc.split(' '):
                term_set.add(term)
    if verbose:
        print('unfiltered: %s' % len(term_set))
    return term_set


def no_punctuations_stats_1(term_set, verbose= False):
    new_term_set = set()

    # No numbers
    for term in term_set:
        term = remove_punctuations(term)
        term = term.strip()  # Trim white spaces
        term = term.split(' ')
        new_term_set |= set(term)
    if verbose:
        print('no punctuation: %s' % len(new_term_set))
    return new_term_set


def no_number_stats_2(term_set, verbose= False):
    new_term_set = set()

    # No numbers
    for term in term_set:
        term = remove_number(term)
        new_term_set.add(term)
    if verbose:
        print('no number: %s' % len(new_term_set))
    return new_term_set


def lower_case_stats_3(term_set, verbose= False):
    new_term_set = set()

    # No numbers
    for term in term_set:
        term = convert_lowercase(term)
        new_term_set.add(term)
    if verbose:
        print('lowercase: %s' % len(new_term_set))
    return new_term_set


def stop_words_stats_4(term_set, verbose= False):
    new_term_set = set()

    # No numbers
    for term in term_set:
        term = remove_stopword(term)
        new_term_set.add(term)
    if verbose:
        print('stopword: %s' % len(new_term_set))
    return new_term_set


def stemming_stats_5(term_set, verbose= False):
    new_term_set = set()

    # No numbers
    for term in term_set:
        term = stem_term(term)
        new_term_set.add(term)
    if verbose:
        print('stemming: %s' % len(new_term_set))
    return new_term_set


def print_preprocessing_stats():
    term_set = unfiltered_stats_0(verbose=True)
    term_set = no_punctuations_stats_1(term_set, verbose=True)
    term_set = no_number_stats_2(term_set, verbose=True)
    term_set = lower_case_stats_3(term_set, verbose=True)
    term_set = stop_words_stats_4(term_set, verbose=True)
    stemming_stats_5(term_set, verbose=True)


def preprocess_doc(doc):
    term_set = set(doc.split(' '))
    term_set = no_punctuations_stats_1(term_set, verbose=False)
    term_set = no_number_stats_2(term_set, verbose=False)
    term_set = lower_case_stats_3(term_set, verbose=False)
    term_set = stop_words_stats_4(term_set, verbose=False)
    term_set = stemming_stats_5(term_set, verbose=False)
    term_set = ' '.join(term_set)  # Convert set to string
    return term_set


def run(doc_names, raw_path, preprocessed_path):
    print('Number of term statistics in all documents..')
    print('--------------------------------------------')
    print_preprocessing_stats()
    print('--------------------------------------------')

    if not os.path.exists(raw_path + '000_flag.flg'):
        print('Pre-processing has been started..')
        old_time = time()
        # Iterate over docs
        for doc_name in doc_names:
            # Open raw file
            with open(raw_path + doc_name, 'r') as doc:
                raw_doc = doc.read()
                raw_doc = string.replace(raw_doc, '\n', ' ')

                # Open new preprocessed file and write preprocessed file
                with open(preprocessed_path + doc_name, 'w') as doc_new:
                    preprocessed_doc = preprocess_doc(raw_doc)
                    doc_new.write(preprocessed_doc)
        temp = open('Emails/Raw/000_flag.flg', 'w')
        temp.close()
        print('Pre-processing took %s min' % str((time() - old_time) / 60.0))
    else:
        print('Pre-processing has already been done!')