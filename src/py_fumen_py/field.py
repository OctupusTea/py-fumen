# -*- coding: utf-8 -*-

from .constant import FieldConstants as Consts
from .operation import Mino, Rotation, Operation

class Field:
    """Keep data of a Tetris playing field."""
    @staticmethod
    def _empty_lines(height):
        empty_lines = [[Mino._] * Consts.WIDTH for y in range(height)]
        return empty_lines[:]

    @staticmethod
    def _to_field_range(slice_=slice(None, None, None)):
        # Convert a normal slice to a suitable range in the field
        return range(
            -Consts.GARBAGE_HEIGHT if slice_.start is None else slice_.start,
            Consts.HEIGHT if slice_.stop is None else slice_.stop,
            1 if slice_.step is None else slice_.step
        )

    @classmethod
    def _field_init(cls, height, field=None):
        # Convert List[str] or str to List[List[Mino]] for __init__
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
        """Create a Field object by parsing or deepcopying the given args.
        Keyword arguments:
        field: the playable part of the field (default=None)
        garbage: the garbage part of the field (default=None)
        """
        self._field = self._field_init(Consts.HEIGHT, field)
        self._garbage = self._field_init(Consts.GARBAGE_HEIGHT, garbage)

    def __getitem__(self, key):
        """Return specified line(s) in the field
        The key can be an int (for one line) or a slice (for a set of lines)
        Negative values in slices are deemed as indexing of garbage lines,
        instead of counting from the end of the field.
        """
        if isinstance(key, slice):
            return [self[y] for y in self._to_field_range(key)]
        elif isinstance(key, int):
            return self._field[key] if key >= 0 else self._garbage[-key-1]
        else:
            raise TypeError(f'Unsupported indexing: {key}')

    def __setitem__(self, key, value):
        """Modify specified line(s) in the field
        The key can be an int (for one line) or a slice (for a set of lines)
        Negative values in slices are deemed as indexing of garbage lines,
        instead of counting from the end of the field.
        """
        if isinstance(key, slice):
            range_ = self._to_field_range(key)
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
        """Return a (deep) copy of the field."""
        return Field(self._field, self._garbage)

    def at(self, x, y):
        """Return the mino at grid (x, y).
        As using Field.__getitem__ requires the ordering field[y][x],
        this method is added for the intuitive field.at(x, y).
        """
        return self[y][x]

    def fill(self, x, y, mino):
        """Modify the mino at grid (x, y) to mino.
        As using Field.__setitem__ requires the ordering field[y][x] = mino,
        this method is added for the intuitive field.fill(x, y, mino).
        """
        self[y][x] = mino

    def is_placeable_at(self, x, y):
        """Test if the desired grid is inside and empty."""
        return (0 <= x < Consts.WIDTH and 0 <= y < Consts.HEIGHT
                and self[y][x] is Mino._)

    def is_placeable(self, operation):
        """Test if the operation locates within empty region."""
        return (operation is None
                or (operation.is_inside()
                    and all(self[y][x] is Mino._
                            for x, y in operation.shape())))

    def is_grounded(self, operation):
        """Test if the operation touches the ground if placed."""
        return (operation is None
                or (self.is_placeable(operation)
                    and not self.is_placeable(operation.shifted(0, -1))))

    def lock(self, operation, forced=False):
        """Lock an operation in place and modify the field.
        Keyword arguments:
        operation
        forced: if the operation should still be placed if it is not located
            in an empty regoin. (default: False)
        """
        if operation is not None:
            if not (forced or self.is_placeable(operation)):
                raise ValueError(f'operation cannot be locked: {operation}')
            for x, y in operation.shape():
                self._field[y][x] = operation.mino

    def drop(self, operation, place=True):
        """Drop an operation to the ground and possibly modify the field.
        Return the dropped (shifted-down) operation
        Keyword arguments:
        operation
        place: if the operation should be locked on the field. (deafult: True)
        """
        if operation is None:
            return None

        shifted_operation = operation.shifted(0, 0)
        for dy in range(1, Consts.HEIGHT):
            shifted_operation = operation.shifted(0, -dy)
            if not self.is_placeable(shifted_operation):
                shifted_operation.shift(0, 1)
                break
        else:
            raise ValueError(f'operation cannot be dropped: {operation}')

        if place:
            self.lock(shifted_operation)
        return shifted_operation

    def rise(self):
        """Rise the garbage line(s) into the playing field and clear the
        garbage line(s).
        """
        self[Consts.GARBAGE_HEIGHT:Consts.HEIGHT]\
            = self[0:Consts.HEIGHT-Conts.GARBAGE_HEIGHT]
        self[0:Consts.GARBAGE_HEIGHT] = self[-Consts.GARBAGE_LINE:0]
        self[-Consts.GARBAGE_HEIGHT:
             0] = self._empty_lines(Consts.GARBAGE_HEIGHT)

    def mirror(self, mirror_color=False):
        """Mirror the field.
        Keyword arguments:
        mirror_color: if the L-J and Z-S color swap should happen. (default:
            False)
        """
        for line in self:
            line[:] = [mino.mirrored() if mirror_color else mino
                       for mino in reversed(line)]

    def shift_up(self, amount=1):
        """Shift the playing field upwards.
        Keyword arguments:
        amount: (default: 1)
        """
        self[amount:] = self[0:Consts.HEIGHT-amount]
        self[0:amount] = self._empty_lines(amount)

    def shift_down(self, amount=1):
        """Shift the playing field downwards.
        Keyword arguments:
        amount: (default: 1)
        """
        self[0:Consts.HEIGHT-amount] = self[amount:]
        self[Consts.HEIGHT-amount:] = self._empty_lines(amount)

    def shift_left(self, amount=1, warp=False):
        """Shift or warp the playing field to the left.
        Keyword arguments:
        amount: (default: 1)
        warp: if the left-most columns should be warpped to the right.
            (default: False)
        """
        for line in self:
            line[:] = (line[amount:]
                       + (line[:amount] if warp else [Mino._]*amount))

    def shift_right(self, amount=1, warp=False):
        """Shift or warp the playing field to the right.
        Keyword arguments:
        amount: (default: 1)
        warp: if the right-most columns should be warpped to the left.
            (default: False)
        """
        for line in self:
            line[:] = ((line[-amount:] if warp else [Mino._]*amount)
                       + line[:-amount])

    def is_lineclear_at(self, y):
        """Test if a line is filled."""
        return Mino._ not in self[y]

    def clear_line(self):
        """Clear filled lines on the field."""
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
        """Apply the suitable flags in an Action class on the field."""
        if action.lock:
            if action.operation.mino.is_colored():
                self.lock(action.operation)
            self.clear_line()
            if action.rise:
                self.rise()
            if action.mirror:
                self.mirror()

    def height(self):
        """Return the y coordinate of the highest non-empty mino."""
        height = Consts.HEIGHT
        while (height > 0
                and all(mino is Mino._ for mino in self[height - 1])):
            height -= 1
        return height

    def _string(self, start=None, stop=None, truncated=True, separator='\n'):
        # Return the string representation of a segment of the field.
        start = -Consts.GARBAGE_HEIGHT if start is None else start
        stop = Consts.HEIGHT if stop is None else stop
        if truncated:
            stop = min(stop, self.height())
        return separator.join(
            reversed([''.join(mino.name for mino in line)
                      for line in self[start:stop]])
        )

    def string(self, truncated=True, separator='\n', with_garbage=True):
        """Return the string representation of the field.
        Keyword arguments:
        truncated: if the blank upper field should be omitted. (default: True)
        separator: the separator between each field line. (default: '\n')
        with_garbage: if the garbage line(s) should be included in the result.
            (default: True)
        """
        return self._string(None if with_garbage else 0, None,
                            truncated, separator)

    def __repr__(self):
        return f'<Field:{self.string(truncated=False, separator=",")}>'

    def __str__(self):
        return self.string()
