# -*- coding: utf-8 -*-

class FieldConstants():
    WIDTH = 10
    HEIGHT = 23
    GARBAGE_HEIGHT = 1
    BLOCK_COUNT = HEIGHT * WIDTH
    TOTAL_HEIGHT = HEIGHT + GARBAGE_HEIGHT
    TOTAL_BLOCK_COUNT = TOTAL_HEIGHT * WIDTH

class FieldConstants110(FieldConstants):
    WIDTH = 10
    HEIGHT = 21
    GARBAGE_HEIGHT = 1
    BLOCK_COUNT = HEIGHT * WIDTH
    TOTAL_HEIGHT = HEIGHT + GARBAGE_HEIGHT
    TOTAL_BLOCK_COUNT = TOTAL_HEIGHT * WIDTH

class FumenStringConstants():
    PREFIX = "v"
    VERSION = "115"
    SUFFIX = "@"
    VERSION_INFO = PREFIX + VERSION + SUFFIX
