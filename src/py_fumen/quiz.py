# -*- coding: utf-8 -*-

from __future__ import annotations

from enum import Enum
import re
from typing import List, Optional

from .operation import Mino

class _QuizOperation(Enum):
    DIRECT = 'direct'
    STOCK = 'stock'
    SWAP = 'swap'

class QuizException(Exception):
    pass

class Quiz:
    @staticmethod
    def create(hold: str='', active:str='', nexts: str='') -> Quiz:
        return Quiz(f'#Q=[{hold}]({active}){nexts}')

    @staticmethod
    def is_quiz_comment(comment: str) -> bool:
        return re.search('^#Q=\[[TIOSZJL]?]\([TIOSZJL]?\)[TIOSZJL]*;?.*$', comment)

    def __init__(self, comment: str):
        if not self.is_quiz_comment(comment):
            raise QuizException(f'Unexpected quiz: {comment}')

        self._hold_piece = comment.split('[', maxsplit=1)[1].split(']', maxsplit=1)[0]
        self._active_piece = comment.split('(', maxsplit=1)[1].split(')', maxsplit=1)[0]
        self._next_pieces = comment.split(')', maxsplit=1)[1].split(';', maxsplit=1)[0]
        self._comment = comment.split(';', maxsplit=1)[1] if ';' in comment else ''

    def _next_piece(self) -> str:
        return self._next_pieces[0:1]

    def _next_residue(self) -> str:
        if len(self._next_pieces) > 1:
            return ';'.join(self._next_pieces[1:], self._comment)
        else:
            return self._comment

    def next_quiz(self, used_piece: Mino) -> Quiz:
        if used_piece.name == self._active_piece:
            return Quiz.create(self._hold_piece, self._next_piece(),
                               self._next_residue())
        if self._hold_piece:
            if used_piece.name == self._hold_piece:
                return Quiz.create(used_piece.name, self._next_piece(),
                                   self._next_residue())
            elif not self._active_piece and used_piece.name == self._next_piece():
                return Quiz.create(self._hold_piece, self._next_residue()[0:1],
                                   self._next_residue()[1:])
        elif used_piece.name == self._next_piece():
            return Quiz.create(used_piece.name, self._next_residue()[0:1],
                               self._next_residue()[1:])

        raise QuizException(f'Unexpected hold piece: {self}')

    def __str__(self) -> str:
        return ''.join([f'#Q[{self._hold_piece}]({self._active_piece})',
                        f'{self._next_pieces}',
                        f';{self._comment}' if self._comment else ''])
