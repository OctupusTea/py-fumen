# -*- coding: utf-8 -*-

from dataclasses import dataclass

from .constant import FieldConstants, FieldConstants110
from .fumen_buffer import FumenBufferReader
from .operation import Mino
from .page import Page, Flags, Refs
from .quiz import Quiz

def _get_reader(string):
    string = string.split('&')[0]
    data = None
    for version in ['115', '110']:
        for prefix in 'vmd':
            match = string.find(prefix+version)
            if match != -1:
                data = string[match+5:].strip().replace('?', '')
                break
        if data:
            break
    else:
        raise ValueError('Unsupported fumen version')

    if version == '110':
        return FumenBufferReader(FieldConstants110, data)
    else:
        return FumenBufferReader(FieldConstants, data)

def decode(string):
    fumen_reader = _get_reader(string)
    pages = []
    prev_comment = ''
    prev_lock = False
    prev_mino = Mino._
    field_ref_index = None
    comment_ref_index = None

    while fumen_reader:
        field, field_modified = fumen_reader.read_field()
        action = fumen_reader.read_action()

        quiz = Quiz(prev_comment)
        if prev_lock:
            quiz.step(prev_mino)

        if action.comment:
            comment = fumen_reader.read_comment()
        else:
            comment = (None if quiz is None else str(quiz)) if pages else ''

        pages.append(Page(
            field=field.copy(),
            operation=(None if action.operation.mino is Mino._
                       else action.operation),
            comment=comment,
            flags=Flags(action.lock, action.mirror, action.colorize,
                        action.rise, (quiz is not None)),
            refs=Refs(field=None if field_modified else field_ref_index,
                      comment=None if action.comment else comment_ref_index)
        ))

        field.apply_action(action)
        if action.comment or len(pages) == 1:
            comment_ref_index = len(pages) - 1
        if field_modified or len(pages) == 1:
            field_ref_index = len(pages) - 1

        prev_comment = comment
        prev_lock = action.lock
        prev_mino = action.operation.mino

    return pages

