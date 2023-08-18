# -*- coding: utf-8 -*-

from .action import Action
from .constant import FieldConstants, FieldConstants110
from .fumen_buffer import FumenBufferReader, FumenBufferWriter
from .js_escape import escape, escaped_compare
from .operation import Mino, Rotation, Operation
from .page import Page, Flags, Refs
from .quiz import Quiz

def _get_reader(string):
    # Initially parse the given input, and preapre the FumenBufferReader.
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
    """Decode the given fumen string into usable data."""
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

def encode(pages):
    """Encode the given pages into a fumen string."""
    fumen_writer = FumenBufferWriter()
    prev_comment = ''
    prev_lock = False
    prev_mino = Mino._

    for page in pages:
        page.flags = Flags() if page.flags is None else page.flags
        page.operation = (
            Operation(Mino._, Rotation.REVERSE, 0, Consts.HEIGHT-1)
            if page.operation is None else page.operation
        )
        quiz = Quiz(prev_comment)
        if prev_lock:
            quiz.step(prev_mino)
        prev_comment = str(quiz)

        fumen_writer.write_field(page.field)
        fumen_writer.write_action(
            Action(page.operation,
            page.flags.rise,
            page.flags.mirror,
            page.flags.colorize,
            not escaped_compare(page.comment, prev_comment, 4095),
            page.flags.lock))
        fumen_writer.write_comment(page.comment, prev_comment)
        prev_comment = page.comment if page.comment else ''
        prev_lock = page.flags.lock
        prev_mino = page.operation.mino

    fumen_writer.move_field_buffer()
    return str(fumen_writer)
