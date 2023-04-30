# -*- coding: utf-8 -*-

import re

RESERVING_CHARS = ("0123456789QWERTYUIOPASDFGHJKLZXCVBNM"
                  "qwertyuiopasdfghjklzxcvbnm@*_+-./")

def escape(string):
    string = '' if string is None else string
    result = ''
    for char in string:
        if char in RESERVING_CHARS:
            result += char
        else:
            char_ord = ord(char)
            result += ('%{0:02X}'.format(char_ord) if char_ord < 256
                       else '%u{0:04X}'.format(char_ord))
    return result

def unescape(string):
    return re.sub(r'%u([a-fA-F0-9]{4})|%([a-fA-F0-9]{2})', _parse, string)

def _parse(match):
    hex_4, hex_2 = match.groups()
    return chr(int(hex_4 if hex_4 else hex_2, 16))

def escaped_compare(a, b, length=None):
    return escape(a)[:length] == escape(b)[:length]
