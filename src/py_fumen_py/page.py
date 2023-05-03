# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Optional

from .field import Field
from .operation import Operation

@dataclass
class Flags():
    """A datacalss for storing decoded page flags.
    Keyword arguments:
    lock: if the operation is locked and filled field lines are cleared.
    mirror: if the field is mirrored.
    colorize: if the page is using SRS coloring. (only valid on page 0.)
    rise: if the garbage in the field rises.
    quiz: if the page's comment is a quiz.
    """
    lock: Optional[bool] = True
    mirror: Optional[bool] = False
    colorize: Optional[bool] = True
    rise: Optional[bool] = False
    quiz: Optional[bool] = False

@dataclass
class Refs():
    """A dataclass for storing decoded page repeating references."""
    field: Optional[int] = None
    comment: Optional[int] = None

@dataclass
class Page():
    """A dataclass for storing decoded page."""
    field: Optional[Field] = None
    operation: Optional[Operation] = None
    comment: Optional[str] = None
    flags: Optional[Flags] = None
    refs: Optional[Refs] = None

    def __repr__(self):
        field_separator = '\n' if self.field else ' '
        return (f'{{field:{field_separator}{self.field}, '
                f'operation: {self.operation}, comment: {self.comment}, '
                f'flags: {self.flags}, refs: {self.refs}}}')
