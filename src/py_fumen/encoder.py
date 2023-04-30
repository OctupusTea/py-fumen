# -*- coding: utf-8 -*-

from .action import ActionEncoder, Action
from .fumen_buffer import FumenBufferWriter
from .js_escape import escape, escaped_compare
from .operation import Mino, Rotation, Operation
from .page import Flags
from .quiz import Quiz

def encode(pages):
    fumen_writer = FumenBufferWriter()
    prev_comment = ''
    prev_lock = False
    prev_mino = Mino._

    for page in pages:
        page.flags = Flags() if page.flags is None else page.flags
        page.operation = (Operation(Mino._, Rotation.REVERSE, 0, 22)
                          if page.operation is None else page.operation)
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
