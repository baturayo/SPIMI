"""
Compress/Decompress terms in a dictionary
"""
from collections import OrderedDict


class CompressedDict:
    def __init__(self):
        self.termsString = ''
        self.ptrString = list([0])
        self.ptrPostingLst = list()

    def insert(self, term, ptrPosting, k=1):
        """
        Insert term and pointer to posting list
        :param term: Key of dict (string)
        :param ptrPosting: posting list of dict (list)
        :param k: Number of blocks for block storage (default is without blocking
        """

        if k == 1:
            self.ptrString.append(len(term) + len(self.termsString))
            self.termsString += term  # Add term to string
            self.ptrPostingLst.append(ptrPosting)  # Add term pointer

        else:
            raise Exception('k parameter must be greater than 0')

    def decompress(self):
        """
        Decompress compressed terms and convert it to an ordered dictionary
        :return:
        """
        decompressedDict = OrderedDict()  # Empty ordered dictionary to store decompressed dictionary
        lenStringPtr = len(self.ptrString)

        for i in range(0, lenStringPtr - 1):
            stringPosInterval = (self.ptrString[i], self.ptrString[i + 1])  # Position interval of the term
            term = self.termsString[stringPosInterval[0]:stringPosInterval[1]]  # Retrieve term from termsString
            decompressedDict[term] = self.ptrPostingLst[i]  # Add posting pointer

        return decompressedDict

# if __name__ == '__main__':
#     compressDict = CompressedDict()
#     compressDict.insert('araba', 1)
#     compressDict.insert('ala', 2)
#     compressDict.insert('azar', 3)
#     compressDict.insert('azbn', 4)
#     print(compressDict.termsString)
#     print(compressDict.ptrString)
#     print(compressDict.ptrPostingLst)
#     a = compressDict.decompress()
#     print(a)
