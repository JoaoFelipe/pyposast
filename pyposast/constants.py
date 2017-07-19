# Copyright (c) 2016 Universidade Federal Fluminense (UFF)
# This file is part of PyPosAST.
# Please, consult the license terms in the LICENSE file.

from __future__ import (absolute_import, division)

import ast
import sys

WHITESPACE = ('\\', '\r', ' ', '\t')
KEYWORDS = ['and', 'or', 'for', 'if', 'lambda', 'None', 'global', 'import',
            'assert', 'try', 'except', 'raise', 'with', 'while', 'del',
            'return', 'class', 'def', 'else', 'finally', 'as']
SEMI_KEYWORDS = []
COMBINED_KEYWORDS = ['is not',  'not in']
FUTURE_KEYWORDS = ['is', 'not']
PAST_KEYWORKDS = {
    'in': 'not',
    'not': 'is'
}

OPERATORS = {
    ast.And: ('and',),
    ast.Or: ('or',),
    ast.Add: ('+', '+='),
    ast.Sub: ('-', '-='),
    ast.Mult: ('*', '*='),
    ast.Div: ('/', '/='),
    ast.Mod: ('%', '%='),
    ast.Pow: ('**', '**='),
    ast.LShift: ('<<', '<<='),
    ast.RShift: ('>>', '>>='),
    ast.BitOr: ('|', '|='),
    ast.BitXor: ('^', '^='),
    ast.BitAnd: ('&', '&='),
    ast.FloorDiv: ('//', '//='),
    ast.Eq: ('==',),
    ast.NotEq: ('!=', '<>'),
    ast.Lt: ('<',),
    ast.LtE: ('<=',),
    ast.Gt: ('>',),
    ast.GtE: ('>=',),
    ast.Is: ('is',),
    ast.IsNot: ('is not',),
    ast.In: ('in',),
    ast.NotIn: ('not in',),
    ast.Invert: ('~',),
    ast.Not: ('not',),
    ast.USub: ('-',),
    ast.UAdd: ('+',),
    ast.Assign: ('=',),
}


if sys.version_info < (3, 0):
    # Python 2
    KEYWORDS += ['exec', 'print', 'from', 'yield']

if sys.version_info >= (3, 0):
    KEYWORDS.append('nonlocal')
    COMBINED_KEYWORDS.append('yield from')
    FUTURE_KEYWORDS.append('yield')
    PAST_KEYWORKDS['from'] = 'yield'

if sys.version_info >= (3, 5):
    # async and await will be promoted to keyword in 3.7
    SEMI_KEYWORDS += ['async', 'await']
    OPERATORS[ast.MatMult] = ('@', '@=')

if sys.version_info >= (3, 6):
    OPERATORS[ast.AnnAssign] = (':', '=')
