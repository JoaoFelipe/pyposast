# Copyright (c) 2015 Universidade Federal Fluminense (UFF)
# This file is part of PyPosAST.
# Please, consult the license terms in the LICENSE file.

from __future__ import (absolute_import, division)

import ast

WHITESPACE = ('\\', '\r', ' ', '\t')
KEYWORDS = ('and', 'or', 'for', 'if', 'lambda', 'None', 'nonlocal',
            'global', 'exec', 'import', 'assert', 'try', 'except', 'raise',
            'with', 'while', 'print', 'del', 'return', 'class', 'def')
COMBINED_KEYWORDS = ('is not', 'yield from', 'not in')
FUTURE_KEYWORDS = ('is', 'yield', 'not')
PAST_KEYWORKDS = {
    'in': 'not',
    'from': 'yield',
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
