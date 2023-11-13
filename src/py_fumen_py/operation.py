# -*- coding: utf-8 -*-

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from .constant import FieldConstants as Consts

class Mino(IntEnum):
    """An IntEnum class representing a mino."""
    _ = 0
    EMPTY = 0
    I = 1
    L = 2
    O = 3
    Z = 4
    T = 5
    J = 6
    S = 7
    X = 8
    G = 8
    GRAY = 8

    @staticmethod
    def parse_name(name):
        """Parse string as mino name and return corresponding Mino.
        This is added beside Mino[name] to account for ' ' and lowercase names.
        The string ' ' (a space) is parsed as Mino._.
        """
        if name == ' ':
            return Mino._
        try:
            return Mino[name.upper()]
        except:
            raise ValueError(f'Unknown mino name: {name}') from None

    def is_colored(self):
        return self is not Mino._ and self is not Mino.X

    def shifted(self, amount, strict=False):
        """Shift the mino numbering by an amount.
        Keyword arguments:
        amount: the shifting amount
        strict: if the out-of-bound values should cause an error.
        """
        if strict:
            return Mino(self+amount)
        else:
            return Mino((self+amount) % len(Mino))

    def mirrored(self):
        return {
            Mino.L: Mino.J,
            Mino.Z: Mino.S,
            Mino.J: Mino.L,
            Mino.S: Mino.Z,
        }.get(self, self)

class Rotation(IntEnum):
    """An IntEnum class representing a rotation."""
    REVERSE = 0
    RIGHT = 1
    R = 1
    CW = 1
    SPAWN = 2
    LEFT = 3
    L = 3
    CCW = 3

    @staticmethod
    def parse_name(name):
        """Parse string as mino name and return corresponding Mino.
        This is added beside Rotation[name] to account for numeric and
        lowercase names.
        The string '0' (zero) is parsed as Rotation.SPAWN.
        The string '2' and '180' is parsed as Rotation.REVERSE.
        """
        rotation = {
            '0': Rotation.SPAWN,
            '2': Rotation.REVERSE,
            '180': Rotation.REVERSE,
        }.get(name, None)
        if rotation is not None:
            return rotation
        try:
            return Rotation[name.upper()]
        except:
            raise KeyError(f'Unknown rotation: {rotation}')

    def short_name(self):
        """Return the common short name used by the community."""
        return ['2', 'R', '0', 'L'][self]

    def shifted(self, amount, strict=False):
        """Shift the rotation numbering by an amount.
        Keyword arguments:
        amount: the shifting amount
        strict: if the out-of-bound values should cause an error.
        """
        if strict:
            return Rotation(self+amount)
        else:
            return Rotation((self+amount) % len(Rotation))

    def mirrored(self):
        return {
            Rotation.RIGHT: Rotation.LEFT,
            Rotation.LEFT: Rotation.RIGHT,
        }.get(self, self)

@dataclass
class Operation():
    """A dataclass for storing information about a tetrimino operation."""
    SHAPES = {
        Mino._: {},
        Mino.I: {Rotation.REVERSE: [[0, 0], [1, 0], [-1, 0], [-2, 0]],
                 Rotation.RIGHT: [[0, 0], [0, 1], [0, -1], [0, -2]],
                 Rotation.SPAWN: [[0, 0], [-1, 0], [1, 0], [2, 0]],
                 Rotation.LEFT: [[0, 0], [0, -1], [0, 1], [0, 2]]},
        Mino.L: {Rotation.REVERSE: [[0, 0], [1, 0], [-1, 0], [-1, -1]],
                 Rotation.RIGHT: [[0, 0], [0, 1], [0, -1], [1, -1]],
                 Rotation.SPAWN: [[0, 0], [-1, 0], [1, 0], [1, 1]],
                 Rotation.LEFT: [[0, 0], [0, -1], [0, 1], [-1, 1]]},
        Mino.O: {Rotation.REVERSE: [[0, 0], [-1, 0], [0, -1], [-1, -1]],
                 Rotation.RIGHT: [[0, 0], [0, -1], [1, 0], [1, -1]],
                 Rotation.SPAWN: [[0, 0], [1, 0], [0, 1], [1, 1]],
                 Rotation.LEFT: [[0, 0], [0, 1], [-1, 0], [-1, 1]]},
        Mino.Z: {Rotation.REVERSE: [[0, 0], [-1, 0], [0, -1], [1, -1]],
                 Rotation.RIGHT: [[0, 0], [0, -1], [1, 0], [1, 1]],
                 Rotation.SPAWN: [[0, 0], [1, 0], [0, 1], [-1, 1]],
                 Rotation.LEFT: [[0, 0], [0, 1], [-1, 0], [-1, -1]]},
        Mino.T: {Rotation.REVERSE: [[0, 0], [1, 0], [-1, 0], [0, -1]],
                 Rotation.RIGHT: [[0, 0], [0, 1], [0, -1], [1, 0]],
                 Rotation.SPAWN: [[0, 0], [-1, 0], [1, 0], [0, 1]],
                 Rotation.LEFT: [[0, 0], [0, -1], [0, 1], [-1, 0]]},
        Mino.J: {Rotation.REVERSE: [[0, 0], [1, 0], [-1, 0], [1, -1]],
                 Rotation.RIGHT: [[0, 0], [0, 1], [0, -1], [1, 1]],
                 Rotation.SPAWN: [[0, 0], [-1, 0], [1, 0], [-1, 1]],
                 Rotation.LEFT: [[0, 0], [0, -1], [0, 1], [-1, -1]]},
        Mino.S: {Rotation.REVERSE: [[0, 0], [1, 0], [0, -1], [-1, -1]],
                 Rotation.RIGHT: [[0, 0], [0, 1], [1, 0], [1, -1]],
                 Rotation.SPAWN: [[0, 0], [-1, 0], [0, 1], [1, 1]],
                 Rotation.LEFT: [[0, 0], [0, -1], [-1, 0], [-1, 1]]},
        Mino.X: {},
    }

    mino: Mino
    rotation: Rotation
    x: int
    y: int

    @classmethod
    def shape_at(cls, mino, rotation, x=0, y=0):
        return [[x+dx, y+dy] for dx, dy
                in cls.SHAPES.get(mino, {}).get(rotation, (0, 0))]

    @classmethod
    def is_inside_at(cls, mino, rotation, x, y):
        return all(0 <= x < Consts.WIDTH
                   and 0 <= y < Consts.HEIGHT
                   for x, y in cls.shape_at(mino, rotation, x, y))

    def shift(self, dx, dy):
        self.x += dx
        self.y += dy

    def shifted(self, dx, dy):
        return Operation(self.mino, self.rotation, self.x+dx, self.y+dy)

    def mirror(self):
        mirrored = self.mirrored()
        self.mino = mirrored.mino
        self.rotation = mirrored.rotation
        self.x = mirrored.x
        self.y = mirrored.y

    def mirrored(self):
        mino = self.mino.mirrored()
        if mino is Mino.I or mino is Mino.O:
            rotation = self.rotation
            if (rotation is Rotation.REVERSE
                    or (rotation is Rotation.LEFT and mino is Mino.O)):
                x = Consts.WIDTH - self.x
            elif rotation is Rotation.SPAWN or mino is Mino.O:
                x = Consts.WIDTH - self.x - 2
            else:
                x = Consts.WIDTH - self.x - 1
        else:
            rotation = self.rotation.mirrored()
            x = Consts.WIDTH - self.x -1
        return Operation(mino, rotation, x, self.y)

    def shape(self):
        return self.shape_at(self.mino, self.rotation, self.x, self.y)

    def is_inside(self):
        return self.is_inside_at(self.mino, self.rotation, self.x, self.y)

