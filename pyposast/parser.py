# Copyright (c) 2016 Universidade Federal Fluminense (UFF)
# This file is part of PyPosAST.
# Please, consult the license terms in the LICENSE file.

from __future__ import (absolute_import, division)

import bisect
import tokenize

from collections import OrderedDict, defaultdict

from .cross_version import StringIO
from .constants import (KEYWORDS, COMBINED_KEYWORDS, SEMI_KEYWORDS,
                        FUTURE_KEYWORDS, PAST_KEYWORKDS)


class ElementDict(OrderedDict):

    def __init__(self, *args, **kwargs):
        super(ElementDict, self).__init__(*args, **kwargs)
        self._bkeys = None

    def set_keys(self):
        if not self._bkeys:
            self._bkeys = list(self.keys())

    def find_next(self, position):
        self.set_keys()
        index = bisect.bisect_left(self._bkeys, position)
        key = self._bkeys[index]
        value = self[key]
        return key, value

    def find_previous(self, position):
        self.set_keys()
        index = bisect.bisect_left(self._bkeys, position)
        key = self._bkeys[index - 1]
        value = self[key]
        return key, value

    def r_find_next(self, position):
        key, value = self.find_next(position)
        return value, key

    def r_find_previous(self, position):
        key, value = self.find_previous(position)
        return value, key


class StackElement(dict):

    def __init__(self, open_str, close_str):
        super(StackElement, self).__init__()
        self.open = open_str
        self.close = close_str
        self.stack = []

    def check(self, t_string, t_srow_scol, t_erow_ecol):
        if t_string == self.open:
            self.stack.append(t_srow_scol)
        elif t_string == self.close:
            self[self.stack.pop()] = t_erow_ecol


def extract_tokens(code, return_tokens=False):
    # Should I implement a LL 1 parser?
    stacks = parenthesis, sbrackets, brackets = [
        StackElement(*x) for x in (('(', ')'), ('[', ']'), ('{', '}'))
    ]
    strings, attributes, numbers = {}, {}, {}
    result = [
        parenthesis, sbrackets, brackets, strings, attributes, numbers,
    ]
    operators = defaultdict(dict)
    names = defaultdict(dict)

    parenthesis_stack = []
    sbrackets_stack = []
    tokens = []
    last = None

    dots = 0 # number of dots
    first_dot = None

    f = StringIO(code)
    for tok in tokenize.generate_tokens(f.readline):
        tokens.append(tok)
        t_type, t_string, t_srow_scol, t_erow_ecol, t_line = tok
        tok = list(tok)
        tok.append(False) # Should wait the next step
        if t_type == tokenize.OP:
            for stack in stacks:
                stack.check(t_string, t_srow_scol, t_erow_ecol)
            if t_string == '.':
                if not dots:
                    first_dot = tok
                dots += 1
                if dots == 3: # Python 2
                    operators['...'][t_erow_ecol] = first_dot[2]
                    dots = 0
                    first_dot = None
            operators[t_string][t_erow_ecol] = t_srow_scol
        elif t_type == tokenize.STRING:
            start = t_srow_scol
            if last and last[0] == tokenize.STRING:
                start = strings[last[3]]
                del strings[last[3]]
            strings[t_erow_ecol] = start
        elif t_type == tokenize.NUMBER:
            numbers[t_erow_ecol] = t_srow_scol
        elif t_type == tokenize.NAME and t_string in KEYWORDS:
            operators[t_string][t_erow_ecol] = t_srow_scol
        elif t_type == tokenize.NAME and dots == 1:
            attributes[t_erow_ecol] = first_dot[2]
            dots = 0
            first_dot = None
        elif t_type == tokenize.NAME and t_string == 'elif':
            operators['if'][t_erow_ecol] = t_srow_scol
        elif t_type == tokenize.NAME and t_string in PAST_KEYWORKDS.keys():
            if last and last[1] == PAST_KEYWORKDS[t_string]:
                combined = "{} {}".format(PAST_KEYWORKDS[t_string], t_string)
                operators[combined][t_erow_ecol] = last[2]
            elif t_string in FUTURE_KEYWORDS:
                tok[5] = True
            else:
                operators[t_string][t_erow_ecol] = t_srow_scol
        elif t_type == tokenize.NAME and t_string in FUTURE_KEYWORDS:
            tok[5] = True
        elif t_string in SEMI_KEYWORDS:
            operators[t_string][t_erow_ecol] = t_srow_scol

        if t_string != '.':
            dots = 0
        if last and last[1] in FUTURE_KEYWORDS and last[5]:
            operators[last[1]][last[3]] = last[2]

        if t_type == tokenize.NAME:
            names[t_string][t_erow_ecol] = t_srow_scol
        if t_type != tokenize.NL:
            last = tok

    if return_tokens:
        return tokens

    result = [ElementDict(sorted(x.items())) for x in result]
    operators = {k: ElementDict(sorted(v.items())) for k, v in operators.items()}
    names = {k: ElementDict(sorted(v.items())) for k, v in names.items()}
    return result, operators, names
