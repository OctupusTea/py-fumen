# -*- coding: utf-8 -*-

from .constant import FieldConstants as Consts
from .operation import Mino, Rotation, Operation

class Field:
    @staticmethod
    def _empty_lines(height):
        return [[Mino._] * Consts.WIDTH for y in range(height)]

    @staticmethod
    def _to_field_range(slice_=slice(None, None, None)):
        return range(
            -Consts.GARBAGE_HEIGHT if slice_.start is None else slice_.start,
            Consts.HEIGHT if slice_.stop is None else slice_.stop,
            1 if slice_.step is None else slice_.step
        )

    @classmethod
    def _field_init(cls, height, field=None):
        if field:
            if isinstance(field, str):
                field = field.splitlines()

            if isinstance(field[0], list):
                lines = [line[:] for line in field]
            elif isinstance(field[0], str):
                lines = [[Mino.parse_name(mino) for mino in line]
                        for line in field[::-1]]
            lines[-1] += [Mino._ for x in range(Consts.WIDTH-len(lines[-1]))]
            lines += cls._empty_lines(height-len(lines))
            return lines
        else:
            return cls._empty_lines(height)

    def __init__(self, field=None, garbage=None):
        self._field = self._field_init(Consts.HEIGHT, field)
        self._garbage = self._field_init(Consts.GARBAGE_HEIGHT, garbage)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return [self[y] for y in self._to_field_range(key)]
        elif isinstance(key, int):
            return self._field[key] if key >= 0 else self._garbage[-key-1]
        else:
            raise TypeError(f'Unsupported indexing: {key}')

    def __setitem__(self, key, value):
        if isinstance(key, slice):
            range_ = self._to_field_range(slice)
            if range_.step == 1:
                if range_.start >= 0 and range_.stop >= 0:
                    self._field[range_.start:range_.stop] = value
                elif range_.start < 0 and range_.stop < 0:
                    self._garbage[-range_.start-1:
                                  -range_.stop-1] = reversed(value)
                elif range_.start < 0 and range_.stop >= 0:
                    self[-range_.start-1:0] = value[:-range_.start]
                    self[0:range_.stop] = value[-range_.start:]
            else:
                for i, line in zip(range_, value, strict=True):
                    self[i] = line
        elif isinstance(key, int):
            if key >= 0:
                self._field[key] = value
            else:
                self._garbage[-key-1] = value
        else:
            raise TypeError(f'Unsupported indexing: {key}')

    def copy(self):
        return Field(self._field, self._garbage)

    def at(self, x, y):
        return self[y][x]

    def fill(self, x, y, mino):
        self[y][x] = mino

    def is_placeable_at(self, x, y):
        return operation.is_inside() and self[y][x] is Mino._

    def is_placeable(self, operation):
        return (operation is None
                or (operation.is_inside()
                    and all(self[y][x] is Mino._
                            for x, y in operation.shape())))

    def is_grounded(self, operation):
        return (operation is None
                or (self.is_placeable(operation)
                    and not self.is_placeable(operation.shifted(0, -1))))

    def lock(self, operation, forced=False):
        if operation is not None:
            if not (forced or self.is_placeable(operation)):
                raise ValueError(f'operation cannot be locked: {operation}')
            for x, y in operation.shape():
                self._field[y][x] = operation.mino

    def drop(self, operation):
        if operation is None:
            return None

        shifted_operation = None
        for dy in range(1, Const.HEIGHT):
            shifted_operation = operation.shifted(0, -dy)
            if not self.is_placeable(shifted_operation):
                shifted_operation.shift(0, 1)
                break
        else:
            raise ValueError(f'operation cannot be dropped: {operation}')

        self.place(self.shifted_operation)
        return shifted_operation

    def rise(self):
        self[Consts.GARBAGE_HEIGHT:Consts.HEIGHT]\
            = self[0:Consts.HEIGHT-Conts.GARBAGE_HEIGHT]
        self[0:Consts.GARBAGE_HEIGHT] = self[-Consts.GARBAGE_LINE:0]
        self[-Consts.GARBAGE_HEIGHT:
             0] = self._empty_lines(Consts.GARBAGE_HEIGHT)

    def mirror(self, mirror_color=False):
        for line in self:
            line[:] = [mino.mirrored() if mirror_color else mino
                       for mino in reversed(line)]

    def shfit_up(self, amount=1):
        self[amount:] = self[0:Consts.HEIGHT-amount]
        self[:amount] = self._empty_lines(amount)

    def shift_down(self, amount=1):
        self[:Consts.HEIGHT-amount] = self[amount:]
        self[Consts.HEIGHT-amount:] = self._empty_lines(amount)

    def shift_left(self, amount=1, warp=False):
        for line in self:
            line[:] = (line[amount:]
                       + (line[:amount] if warp else [Mino._]*amount))

    def shift_right(self, amount=1, warp=False):
        for line in self:
            line[:] = ((line[-amount:] if warp else [Mino._]*amount)
                       + line[:-amount])

    def is_lineclear_at(self, y):
        return Mino._ not in self[y]

    def clear_line(self):
        lines = []
        n_lineclear = 0
        for line in self:
            if Mino._ in line:
                lines.append(line)
            else:
                n_lineclear += 1
        self._field = lines + self._empty_lines(n_lineclear)
        return n_lineclear

    def apply_action(self, action):
        if action.lock:
            if action.operation.mino.is_colored():
                self.lock(action.operation)
            self.clear_line()
            if action.rise:
                self.rise()
            if action.mirror:
                self.mirror()

    def height(self):
        height = Consts.HEIGHT
        while (height > 0
                and all(mino is Mino._ for mino in self[height - 1])):
            height -= 1
        return height

    def _string(self, start=None, stop=None, truncated=True, separator='\n'):
        start = -Consts.GARBAGE_HEIGHT if start is None else start
        stop = Consts.HEIGHT if stop is None else stop
        if truncated:
            stop = min(stop, self.height())
        return separator.join(
            reversed([''.join(mino.name for mino in line)
                      for line in self[start:stop]])
        )

    def string(self, truncated=True, separator='\n', with_garbage=True):
        return self._string(None if with_garbage else 0, None,
                            truncated, separator)

    def __repr__(self):
        return f'<Field:{self.string(truncated=False, separator=",")}>'

    def __str__(self):
        return self.string()
