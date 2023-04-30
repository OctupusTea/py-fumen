# -*- coding: utf-8 -*-

class FieldConstants:
    GARBAGE_HEIGHT = 1
    WIDTH = 10
    HEIGHT = 23
    BLOCK_COUNT = WIDTH * HEIGHT
    TOTAL_HEIGHT = HEIGHT + GARBAGE_HEIGHT
    TOTAL_BLOCK_COUNT = TOTAL_HEIGHT * WIDTH

class FieldConstants110:
    GARBAGE_HEIGHT = 1
    WIDTH = 10
    HEIGHT = 21
    BLOCK_COUNT = WIDTH * HEIGHT
    TOTAL_HEIGHT = HEIGHT + GARBAGE_HEIGHT
    TOTAL_BLOCK_COUNT = TOTAL_HEIGHT * WIDTH

class FumenStringConstants:
    PREFIX = "v"
    VERSION = "115"
    SUFFIX = "@"
    VERSION_INFO = PREFIX + VERSION + SUFFIX
    BLOCK_SIZE = 47
