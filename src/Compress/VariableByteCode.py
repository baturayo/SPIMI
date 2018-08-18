"""
Compress posting list with variable byte code
"""
from struct import pack, unpack


class VariableByteCode:
    def __init__(self):
        pass

    @staticmethod
    def VB_encode_number(num):
        """
        Encode Gaps with Variable Byte encoding
        :param num: integer gaps
        :return: encoded bytes
        """
        bytes_list = []
        while True:
            bytes_list.insert(0, num % 128)
            if num < 128:
                break
            num = num // 128
        bytes_list[-1] += 128
        return pack('%dB' % len(bytes_list), *bytes_list)

    def VB_encode(self, nums):
        """
        Encode an array of integers with variable byte encoding
        :param nums: Integer array
        :return: Encoded integer array
        """
        bytes_list = []
        for number in nums:
            bytes_list.append(self.VB_encode_number(number))
        return b"".join(bytes_list)

    @staticmethod
    def VB_decode(bytestream):
        """
        Convert encoded byte array into integer array
        :param bytestream: Array of encoded bytes
        :return: Array of integers
        """
        n = 0
        numbers = []
        bytestream = unpack('%dB' % len(bytestream), bytestream)
        for byte in bytestream:
            if byte < 128:
                n = 128 * n + byte
            else:
                n = 128 * n + (byte - 128)
                numbers.append(n)
                n = 0
        return numbers


# if __name__ == '__main__':
#     a = VariableByteCode()
#     b = a.VB_encode([1000000])
#     a.VB_decode(b)
