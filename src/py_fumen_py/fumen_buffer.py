# -*- coding: utf-8 -*-

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Deque

from .action import Action, ActionCodec
from .comment import CommentCodec
from .constant import FieldConstants, FumenStringConstants
from .field import Field
from .js_escape import escape, unescape

class FumenBuffer(deque):
    """The buffer for fumen data.
    deque is used for faster element removal from the front.
    """
    ENCODING_TABLE = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                      'abcdefghijklmnopqrstuvwxyz0123456789+/')
    DECODING_TABLE = {char: i for i, char in enumerate(ENCODING_TABLE)}
    TABLE_LENGTH = len(ENCODING_TABLE)

    def __init__(self, data=''):
        """Create a FumenBuffer object with the given data."""
        try:
            super().__init__(self.DECODING_TABLE[char] for char in data)
        except KeyError as e:
            raise ValueError(f'Unsupported fumen string character: {e}') from None

    def poll(self, poll_length):
        """Return the value represented by poll_length symbols at the front.
        The symbol ordering is big-endian.
        """
        poll_stack = []
        try:
            for i in range(poll_length):
                poll_stack.append(self.popleft())
        except IndexError as e:
            raise ValueError(f'Cannot poll {poll_length} items: '
                             f'only {len(poll_stack)} present') from None

        value = 0
        while poll_stack:
            value = poll_stack.pop() + value * self.TABLE_LENGTH
        return value

    def push(self, value, push_length=1):
        """Push the value with push_length symbols representing it.
        The symbol ordering is big-endian.
        """
        for i in range(push_length):
            value, remainder = divmod(value, self.TABLE_LENGTH)
            self.append(remainder)

    def fumen_string(self, prefix=FumenStringConstants.VERSION_INFO,
            block_size=FumenStringConstants.BLOCK_SIZE):
        """Return the stored symbol(s) as a fumen string.
        Keyword arguments:
        prefix: fumen string previx. (default: the deafult VERSION_INFO 'v115')
        block_size: Insert a '?' every block_size of characters. (default: the
            default BLOCK_SIZE 47)
        """
        string = ''.join([prefix, repr(self)])
        if len(string) < block_size:
            return string
        else:
            return '?'.join(string[i:i+block_size]
                            for i in range(0, len(string), block_size))

    def __iadd__(self, other):
        """Append another FumenBuffer at the back of self."""
        for item in other:
            self.append(item)
        return self

    def __str__(self):
        return self.fumen_string()

    def __repr__(self):
        return ''.join(self.ENCODING_TABLE[value] for value in self)

class FumenBufferReader(FumenBuffer):
    def __init__(self, consts, data=''):
        """Create a FumenBufferReader object with given data."""
        super().__init__(data)
        self._consts = consts
        self._field_previous = Field()
        self._field_repeat_count = -1
        self._comment_previous = None

    def _apply_field_diff(self, index, diff, length):
        # Apply the decoded field diff on the stored field.
        if diff != 8:
            diff -= 8
            for i in range(index, index+length+1):
                y, x = divmod(i, self._consts.WIDTH)
                y = self._consts.HEIGHT - y - 1
                self._field_previous.fill(
                    x, y, self._field_previous.at(x, y).shifted(diff)
                )

    def read_field(self):
        """Read one playing field from the data.
        Return a new or repeated Field object.
        """
        if self._field_repeat_count > 0:
            self._field_repeat_count -= 1
            return self._field_previous, False

        diff, length = divmod(self.poll(2),
                              self._consts.TOTAL_BLOCK_COUNT)
        if diff == 8 and length == self._consts.TOTAL_BLOCK_COUNT - 1:
            self._field_repeat_count = self.poll(1)
            return self._field_previous, False
        else:
            self._apply_field_diff(0, diff, length)
            field_index = length + 1

            while field_index < self._consts.TOTAL_BLOCK_COUNT:
                diff, length = divmod(self.poll(2),
                                      self._consts.TOTAL_BLOCK_COUNT)
                self._apply_field_diff(field_index, diff, length)
                field_index += length + 1
            return self._field_previous, True

    def read_action(self):
        """Read one Action object from the data."""
        return ActionCodec.decode(self._consts, self.poll(3))

    def read_comment(self):
        """Read one variable-lenght comment string from the data."""
        length = self.poll(2)
        comment = unescape(CommentCodec.decode(
            [self.poll(5) for i in range((length+3)//4)]
        )[:length])
        self._comment_previous = comment
        return comment

class FumenBufferWriter(FumenBuffer):
    def __init__(self, consts=FieldConstants):
        """Create a FumenBufferWriter object with an empty buffer."""
        super().__init__()
        self._consts = consts
        self._field_previous = Field()
        self._field_repeat_count = -1
        self._field_repeat_buffer = FumenBuffer()

    def _field_diff(self, field, x, y):
        # Return the difference between previous and current field at (x, y)
        y = self._consts.HEIGHT - y - 1
        return field.at(x, y) - self._field_previous.at(x, y)

    def _write_field_diff(self, diff, length):
        self._field_repeat_buffer.push(
            (diff+8)*self._consts.TOTAL_BLOCK_COUNT+length, 2
        )

    def move_field_buffer(self):
        """Move the additional buffer for field repeating count.
        Due to the slow random access of deque, one additional buffer is used
        to account for incoming data after wrting a repeating count.
        One should call this method before outputting fumen string to avoid
        incorrect results.
        """
        self += self._field_repeat_buffer
        self._field_repeat_buffer.clear()

    def write_field(self, field):
        """Write the given field to the buffer."""
        if field is None:
            diff = 0
            prev_diff = 0
            length = self._consts.TOTAL_BLOCK_COUNT - 1
        else:
            prev_diff = self._field_diff(field, 0, 0)
            length = -1
            for y in range(self._consts.TOTAL_HEIGHT):
                for x in range(self._consts.WIDTH):
                    diff = self._field_diff(field, x, y)
                    if diff != prev_diff:
                        self._write_field_diff(prev_diff, length)
                        length = 0
                        prev_diff = diff
                    else:
                        length += 1

        if diff or length != self._consts.TOTAL_BLOCK_COUNT - 1:
            self._write_field_diff(prev_diff, length)
            self.move_field_buffer()
            self._field_repeat_count = -1
            self._field_previous = field.copy()
        elif 0 <= self._field_repeat_count < self.TABLE_LENGTH - 1:
            self[-1] += 1
            self._field_repeat_count += 1
        else:
            self._field_repeat_count = 0
            self._write_field_diff(prev_diff, length)
            self._field_repeat_buffer.push(self._field_repeat_count, 1)
            self.move_field_buffer()

    def write_action(self, action):
        """Write the given action and apply it to the previous field."""
        self._field_repeat_buffer.push(
            ActionCodec.encode(self._consts, action), 3)
        self._field_previous.apply_action(action)

    def write_comment(self, comment, prev_comment):
        """Write the given comment to the buffer.
        Return whether the comment is different from the previous one.
        """
        comment = escape(comment)[:4095]
        prev_comment = escape(prev_comment)[:4095]

        if comment != prev_comment:
            length, encoded_comments = CommentCodec.encode(comment)
            self._field_repeat_buffer.push(length, 2)
            for value in encoded_comments:
                self._field_repeat_buffer.push(value, 5)
            return True
        else:
            return False
