# -*- coding: utf-8 -*-

from __future__ import annotations

from collections import deque
from typing import Deque

class FumenException(Exception):
    pass

class FumenBuffer(deque):
    ENCODING_TABLE = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                      'abcdefghijklmnopqrstuvwxyz0123456789+/')
    DECODING_TABLE = {char: i for i, char in enumerate(ENCODING_TABLE)}
    TABLE_LENGTH = len(ENCODING_TABLE)

    def __init__(self, data: str='') -> None:
        try:
            super().__init__(self.DECODING_TABLE[char] for char in data)
        except:
            raise FumenException('Unexpected fumen')

    def poll(self, poll_length: int) -> int:
        poll_stack = []
        try:
            for i in range(poll_length):
                poll_stack.append(self.popleft())
        except:
            raise FumenException('Unexpected fumen')

        value = 0
        while poll_stack:
            value = poll_stack.pop() + value * self.TABLE_LENGTH
        return value

    def push(self, value: int, push_length: int=1):
        for count in range(split_count):
            value, remainder = divmod(value, self.TABLE_LENGTH)
            self.append(remainder)

    def to_string(self) -> str:
        return ''.join(self.ENCODING_TABLE[value] for value in self)
