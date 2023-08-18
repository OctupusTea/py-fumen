# -*- coding: utf-8 -*-

from dataclasses import dataclass

from .constant import FieldConstants
from .operation import Mino, Rotation, Operation

@dataclass
class Action():
    """A dataclass for storing encoded Fumen page flags and field changes.
    Keyword arguments:
    operation: the operation applied to the field.
    rise: if the garbage in the field rises.
    mirror: if the field is mirrored.
    colorize: if the page is using SRS coloring. (only valid on page 0.)
    lock: if the operation is locked and filled field lines are cleared.
    """
    operation: Operation
    rise: bool
    mirror: bool
    colorize: bool
    comment: bool
    lock: bool

class ActionCodec() :
    """Codec of the dataclass Action, from/to fumen data (int).
    """
    _DECODING_OFFSET = {
        Mino.I: {
            Rotation.REVERSE: (1, 0),
            Rotation.LEFT: (0, -1),
        },
        Mino.O: {
            Rotation.SPAWN: (0, -1),
            Rotation.REVERSE: (1, 0),
            Rotation.LEFT: (1, -1),
        },
        Mino.Z: {
            Rotation.SPAWN: (0, -1),
            Rotation.LEFT: (1, 0),
        },
        Mino.S: {
            Rotation.SPAWN: (0, -1),
            Rotation.RIGHT: (-1, 0),
        },
    }

    _ENCODING_OFFSET = {
        Mino.I: {
            Rotation.REVERSE: (-1, 0),
            Rotation.LEFT: (0, 1),
        },
        Mino.O: {
            Rotation.SPAWN: (0, 1),
            Rotation.REVERSE: (-1, 0),
            Rotation.LEFT: (-1, 1),
        },
        Mino.Z: {
            Rotation.SPAWN: (0, 1),
            Rotation.LEFT: (-1, 0),
        },
        Mino.S: {
            Rotation.SPAWN: (0, 1),
            Rotation.RIGHT: (1, 0),
        },
    }

    @classmethod
    def _decode_coords(cls, consts, encoded_coords, mino, rotation):
        dx, dy = cls._DECODING_OFFSET.get(mino, {}).get(rotation, (0, 0))
        return (dx + encoded_coords % consts.WIDTH,
                dy + consts.HEIGHT - encoded_coords // consts.WIDTH - 1)

    @classmethod
    def decode(cls, consts, encoded_action):
        q, r = divmod(encoded_action, 8)
        mino = Mino(r)
        q, r = divmod(q, 4)
        rotation = Rotation(r)
        q, r = divmod(q, consts.TOTAL_BLOCK_COUNT)
        x, y = cls._decode_coords(consts, r, mino, rotation)
        q, r = divmod(q, 2)
        rise = bool(r)
        q, r = divmod(q, 2)
        mirror = bool(r)
        q, r = divmod(q, 2)
        colorize = bool(r)
        q, r = divmod(q, 2)
        comment = bool(r)
        q, r = divmod(q, 2)
        lock = not bool(r)

        return Action(operation=Operation(mino=mino, rotation=rotation,
                                          x=x, y=y),
                      rise=rise, mirror=mirror, colorize=colorize,
                      comment=comment, lock=lock)

    @staticmethod
    def _encode_rotation(operation):
        if operation.mino.is_colored():
            return operation.rotation.value
        else:
            return 0

    @classmethod
    def _encode_coords(cls, consts, operation):
        dx, dy = cls._ENCODING_OFFSET.get(
            operation.mino, {}
        ).get(operation.rotation, (0, 0))
        x, y = ((dx + operation.x, dy + operation.y)
                if operation.mino.is_colored() else (0, Consts.HEIGHT-1))
        return (consts.HEIGHT - y - 1) * consts.WIDTH + x

    @classmethod
    def encode(cls, consts, action):
        encoded_action = int(not action.lock)
        encoded_action *= 2
        encoded_action += bool(action.comment)
        encoded_action *= 2
        encoded_action += bool(action.colorize)
        encoded_action *= 2
        encoded_action += bool(action.mirror)
        encoded_action *= 2
        encoded_action += bool(action.rise)
        encoded_action *= consts.TOTAL_BLOCK_COUNT
        encoded_action += cls._encode_coords(consts, action.operation)
        encoded_action *= 4
        encoded_action += cls._encode_rotation(action.operation)
        encoded_action *= 8
        encoded_action += action.operation.mino

        return encoded_action
