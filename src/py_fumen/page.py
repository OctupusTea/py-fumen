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
    field: Optional[Field]
    operation: Optional[Operation]
    comment: Optional[str]
    flags: Optional[Flags]
    refs: Optional[Refs]

    def __repr__(self):
        return (f'{{field:\n{self.field}, operation: {self.operation}, '
                f'comment:{self.comment}, flags: {self.flags}, '
                f'refs: {self.refs}}}')
