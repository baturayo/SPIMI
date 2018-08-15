"""
Compress posting list with gamma code
"""
from bitstring import BitArray


class GammaCode:
    def __init__(self):
        pass

    def __unary_code(self, num):
        """
        Find unary code of num value
        :param num: Integer
        :return: Unary code of given integer
        """
        unaryCode = ''.join('1' for _ in range(0, num))
        unaryCode += '0'
        return unaryCode

    def gamma_encode_number(self, num):
        """
        Find gamma code of a given number
        :param num: Integer
        :return: binary gamma code
        """
        bin_value = bin(num)
        offset = bin_value[3:]  # Delete 0b and leading one
        length = self.__unary_code(len(offset))  # Find unary code of the length of offset
        gamma_code = '0b' + length + offset  # Append length and offset
        gamma_code = BitArray(gamma_code)
        return gamma_code

    def gamma_encode(self, nums):
        """
        Find gamma code for all elements in an integer array
        :param nums: integer array
        :return: Gamma encoded binary
        """
        binary_posting = ''
        for num in nums:
            binary_posting += self.gamma_encode_number(num)
        bitStream = '0b' + binary_posting
        return bitStream

    def gamma_decode(self, bitStream):
        """
        Convert gamma encoding to integer array by decoding
        :param bitStream: binary bit stream
        :return: integer array
        """
        decoded_lst = list()
        isUnaryBlock = True
        decoded_unary = 0
        counter = 0
        offset = ''

        for bin_value in bitStream.bin:  # Convert bit stream into binary
            if isUnaryBlock:  # Unary Block
                if int(bin_value) == 1:
                    counter += 1
                elif int(bin_value) == 0:  # if bin_value == 0
                    # SPECIAL CASE: If first element of unary is 0, it means that gamma code is 1
                    if counter == 0:
                        decoded_lst.append(1)

                    else:
                        isUnaryBlock = False
                        decoded_unary = counter
                        counter = 0
                else:
                    raise Exception('Input must be binary!')

            else:  # Offset Block
                counter += 1
                offset += bin_value
                if counter == decoded_unary:
                    offset = '1' + offset  # Append leading 1 back
                    decoded_lst.append((int(offset, 2)))
                    isUnaryBlock = True
                    counter = 0
                    offset = ''
        return decoded_lst

#
# if __name__ == '__main__':
#     a = GammaCode()
#     b = a.gamma_encode([10, 25, 30, 88])
#     print(b)
#     c = a.gamma_decode(b)
#     print (c)
