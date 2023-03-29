# -*- coding: utf-8 -*-

from typing import List

class CommentCodec():
    ENCODING_TABLE = (' !"#$%&\'()*+,-./0123456789:;<=>?@'
                      'ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`'
                      'abcdefghijklmnopqrstuvwxyz{|}~')
    DECODING_TABLE = {char: i for i, char in enumerate(ENCODING_TABLE)}
    TABLE_LENGTH = len(ENCODING_TABLE) + 1

    def decode(encoded_comments: List[int]) -> str:
        string = ''

        for value in encoded_comments:
            for i in range(4):
                value, ch = divmod(value, self.TABLE_LENGTH)
                string += ENCODING_TABLE[ch]

        return string

    def encode(comment: str) -> int, List[int]:
        result = []
        length = len(comment)

        for i in range(0, length, 4):
            value = 0
            for char in reversed(comment[i:i+4]):
                value = DECODING_TABLE[char] + value * self.TABLE_LENGTH
            result.append(value)

        return length, result
