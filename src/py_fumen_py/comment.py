# -*- coding: utf-8 -*-

class CommentCodec:
    _ENCODING_TABLE = (' !"#$%&\'()*+,-./0123456789:;<=>?@'
                      'ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`'
                      'abcdefghijklmnopqrstuvwxyz{|}~')
    _DECODING_TABLE = {char: i for i, char in enumerate(_ENCODING_TABLE)}
    _TABLE_LENGTH = len(_ENCODING_TABLE) + 1

    @classmethod
    def decode(cls, encoded_comments):
        string = ''

        for value in encoded_comments:
            for i in range(4):
                value, ch = divmod(value, cls._TABLE_LENGTH)
                string += cls._ENCODING_TABLE[ch]

        return string

    @classmethod
    def encode(cls, comment):
        result = []
        length = len(comment)

        for i in range(0, length, 4):
            value = 0
            for char in reversed(comment[i:i+4]):
                value = cls._DECODING_TABLE[char] + value * cls._TABLE_LENGTH
            result.append(value)

        return length, result

