# -*- coding: utf-8 -*-

class FieldConstants:
    """Default field constants for version 115 and onwards.
    """
    GARBAGE_HEIGHT = 1
    WIDTH = 10
    HEIGHT = 23
    BLOCK_COUNT = WIDTH * HEIGHT
    TOTAL_HEIGHT = HEIGHT + GARBAGE_HEIGHT
    TOTAL_BLOCK_COUNT = TOTAL_HEIGHT * WIDTH

class FieldConstants110:
    """Default field constants for version 110.
    """
    GARBAGE_HEIGHT = 1
    WIDTH = 10
    HEIGHT = 21
    BLOCK_COUNT = WIDTH * HEIGHT
    TOTAL_HEIGHT = HEIGHT + GARBAGE_HEIGHT
    TOTAL_BLOCK_COUNT = TOTAL_HEIGHT * WIDTH

class FumenStringConstants:
    """Constants of the 'v115@' prefix in a encoded fumen string
    """
    PREFIX = "v"
    VERSION = "115"
    SUFFIX = "@"
    VERSION_INFO = PREFIX + VERSION + SUFFIX
    BLOCK_SIZE = 47
