# -*- coding: utf-8 -*-

import copy

class Quiz:
    """A class for dealing the comment as a quiz if possible.
    Note that this class is largely differnt from tetris-fumen.Quiz.
    This class is more similar to the quiz system on fumen.zui.jp.
    """
    @staticmethod
    def parse_comment(comment):
        """Extract quiz information from the comment.
        Substring after the first ';' is deemed as the residue.
        Only 'IOLZTJS()[]' are considered valid characters for the following:
            Substring between '[' and ']' is deemed as the held mino.
            Substring between '(' and ')' is deemed as the active mino.
            The rest is deemed as the next queue.
        """
        if isinstance(comment, str):
            if not comment.startswith('#Q='):
                return False, None, None, None, comment

            try:
                quiz_string, residue = comment.split(';', maxsplit=1)
            except:
                quiz_string = comment
                residue = ''
            quiz_string = ''.join(ch for ch in comment if ch in 'IOLZTJS()[]')

            hold = quiz_string.split('[', maxsplit=1)[1].split(']')[0]
            active = quiz_string.split('(', maxsplit=1)[1].split(')')[0]
            nexts = ''.join(ch for ch in quiz_string.split(')', maxsplit=1)[1]
                            if ch in 'IOLZTJS')

            return True, hold, active, nexts, residue
        else:
            raise TypeError('Unsupported comment type')

    def __init__(self, comment):
        """Create a Quiz object with the given comment."""
        if isinstance(comment, str):
            (self._is_valid, self._hold, self._active, self._nexts,
                self._residue) = self.parse_comment(comment)
        else:
            raise TypeError('Unsupported comment type')

    def _split_nexts(self, split_index=1):
        """Return the split of nexts at split_index."""
        return (self._nexts[split_index-1:split_index],
                self._nexts[split_index:])

    def copy(self):
        """Return a (deep) copy of the quiz."""
        return copy.copy(self)

    def refresh(self):
        """Re-interpret the stored data as a quiz."""
        (self._is_valid, self._hold, self._active, self._nexts,
            self._residue) = self.parse_comment(str(self))

    def step(self, mino):
        """Modify the stored data according to the given mino and refresh.
        Nothing happens if the stored data is invalid or the mino is Mino._ or
        Mino.X.
        """
        if self._is_valid and mino.is_colored():
            if mino.name == self._active:
                self._active, self._nexts = self._split_nexts()
            elif mino.name == self._hold:
                self._hold, self._active, self._nexts = (
                    self._active, *self._split_nexts())
            elif mino.name == self._nexts[0]:
                if not self._hold:
                    self._hold, self._active, self._nexts = (
                        self._active, *self._split_nexts(2))
                elif not self._active:
                    self._active, self._nexts = self._split_nexts(2)
            self.refresh()

    @property
    def is_valid(self):
        return self._is_valid

    @property
    def hold(self):
        return self._hold

    @property
    def active(self):
        return self._active

    @property
    def nexts(self):
        return self._nexts

    @property
    def residue(self):
        return self._residue

    def __len__(self):
        return len(self._hold) + len(self._active) + len(self._nexts)

    def __bool__(self):
        """The functinoal equivalent of Quiz.canOperate() in tetris-fumen.
        Return whether the stored data is valid after refresh.
        """
        return True if len(self) else self.parse_comment(self._residue)[0]

    def __repr__(self):
        if self._active:
            return ''.join([f'#Q=[{self._hold}]({self._active}){self._nexts}',
                            f';{self._residue}' if self._residue else ''])
        else:
            return self._residue
