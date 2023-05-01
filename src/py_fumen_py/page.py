# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Optional

from .field import Field
from .operation import Operation

@dataclass
class Flags():
    lock: Optional[bool] = True
    mirror: Optional[bool] = False
    colorize: Optional[bool] = True
    rise: Optional[bool] = False
    quiz: Optional[bool] = False

@dataclass
class Refs():
    field: Optional[int] = None
    comment: Optional[int] = None

@dataclass
class Page():
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
