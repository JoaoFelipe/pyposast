# Copyright (c) 2016 Universidade Federal Fluminense (UFF)
# This file is part of PyPosAST.
# Please, consult the license terms in the LICENSE file.

import sys

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO


class SelectVersion(object):

    def __init__(self, compare_func):
        self.compare_func = compare_func

    def __call__(self, fn):
        def inner(*args, **kwargs):
            if self.compare_func(sys.version_info):
                return fn(*args, **kwargs)
            return None
        return inner

    def __bool__(self):
        return self.compare_func(sys.version_info)

    def __nonzero__(self):
        return self.__bool__()

try:
    iter([]).next
except AttributeError:
    def iternext(seq):
        """Get the `next` function for iterating over `seq`."""
        return iter(seq).__next__
else:
    def iternext(seq):
        """Get the `next` function for iterating over `seq`."""
        return iter(seq).next

only_python2 = SelectVersion(lambda x: x < (3, 0))
only_python3 = SelectVersion(lambda x: x >= (3, 0))
only_python35 = SelectVersion(lambda x: x >= (3, 5))
only_python36 = SelectVersion(lambda x: x >= (3, 6))

if only_python3:
    from tokenize import detect_encoding

    readlines = lambda seq: iter(seq).__next__

if only_python2:
    import re
    from codecs import lookup, BOM_UTF8
    cookie_re = re.compile(r'^[ \t\f]*#.*coding[:=][ \t]*([-\w.]+)', re.L)
    blank_re = re.compile(br'^[ \t\f]*(?:[#\r\n]|$)', re.L)

    def _get_normal_name(orig_enc):
        """Extracted from Python 3.5.0/Lib/tokenize.py for compability"""
        # Only care about the first 12 characters.
        enc = orig_enc[:12].lower().replace("_", "-")
        if enc == "utf-8" or enc.startswith("utf-8-"):
            return "utf-8"
        if enc in ("latin-1", "iso-8859-1", "iso-latin-1") or \
           enc.startswith(("latin-1-", "iso-8859-1-", "iso-latin-1-")):
            return "iso-8859-1"
        return orig_enc

    def detect_encoding(readline):
        """Extracted from Python 3.5.0/Lib/tokenize.py for compability"""
        bom_found = False
        encoding = None
        default = 'ascii'

        def read_or_stop():
            try:
                return readline()
            except StopIteration:
                return b''

        def find_cookie(line):
            try:
                line_string = line.decode('ascii')
            except UnicodeDecodeError:
                return None

            match = cookie_re.match(line_string)
            if not match:
                return None
            encoding = _get_normal_name(match.group(1))
            try:
                lookup(encoding)
            except LookupError:
                # This behaviour mimics the Python interpreter
                raise SyntaxError("unknown encoding: " + encoding)

            if bom_found:
                if encoding != 'utf-8':
                    # This behavior mimics the Python interpreter
                    raise SyntaxError('encoding problem: utf-8')
                encoding += '-sig'
            return encoding

        first = read_or_stop()
        if first.startswith(BOM_UTF8):
            bom_found = True
            first = first[3:]
            default = 'utf-8-sig'
        if not first:
            return default, []

        encoding = find_cookie(first)
        if encoding:
            return encoding, [first]
        if not blank_re.match(first):
            return default, [first]

        second = read_or_stop()
        if not second:
            return default, [first]

        encoding = find_cookie(second)
        if encoding:
            return encoding, [first, second]

        return default, [first, second]

    readlines = lambda seq: iter(seq).next


def decode_source_to_unicode(source_bytes):
    encoding = detect_encoding(readlines(source_bytes.splitlines(True)))
    return source_bytes.decode(encoding[0], 'replace')


def native_decode_source(text):
    """Use codec specified in file to decode to unicode
    Then, encode unicode to native str:
        Python 2: bytes
        Python 3: unicode
    """
    if ((only_python3 and isinstance(text, bytes))
            or (only_python2 and isinstance(text, str))):
        text = decode_source_to_unicode(text)
    if only_python2:
        return text.encode('ascii', 'replace')
    return text
