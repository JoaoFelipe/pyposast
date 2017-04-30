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


def apply_delta(original, dline, doffset):
    return (original[0] + dline, original[1] + doffset)


class TokenCollector(object):

    def __init__(self):
        self.stacks = self.parenthesis, self.sbrackets, self.brackets = [
            StackElement(*x) for x in (('(', ')'), ('[', ']'), ('{', '}'))
        ]
        self.strings, self.attributes, self.numbers = {}, {}, {}
        self.operators = defaultdict(dict)
        self.names = defaultdict(dict)
        self.tokens = []

    def loop(self, code, dline=0, doffset=0):
        last = None
        dots = 0 # number of dots
        first_dot = None

        f = StringIO(code)
        for tok in tokenize.generate_tokens(f.readline):
            self.tokens.append(tok)
            t_type, t_string, t_srow_scol, t_erow_ecol, t_line = tok
            # ToDo: apply delta
            t_srow_scol = apply_delta(t_srow_scol, dline, doffset)
            t_erow_ecol = apply_delta(t_erow_ecol, dline, doffset)
            tok = [t_type, t_string, t_srow_scol, t_erow_ecol, t_line]
            tok.append(False) # Should wait the next step
            if t_type == tokenize.OP:
                for stack in self.stacks:
                    stack.check(t_string, t_srow_scol, t_erow_ecol)
                if t_string == '.':
                    if not dots:
                        first_dot = tok
                    dots += 1
                    if dots == 3: # Python 2
                        self.operators['...'][t_erow_ecol] = first_dot[2]
                        dots = 0
                        first_dot = None
                self.operators[t_string][t_erow_ecol] = t_srow_scol
            elif t_type == tokenize.STRING:
                if t_string.startswith('f'): # Python 3.6
                    inner = t_string[2:-1]
                    stack = []
                    for index, char in enumerate(inner):
                        if char == "{":
                            if not stack or stack[-1] != index - 1:
                                stack.append(index)
                        if char == "}" and stack:
                            oindex = stack.pop()
                            sub = inner[oindex + 1:index]
                            self.brackets.check(
                                "{",
                                apply_delta(t_srow_scol, 0, oindex + 2),
                                apply_delta(t_srow_scol, 0, oindex + 3),
                            )
                            self.brackets.check(
                                "}",
                                apply_delta(t_srow_scol, 0, index + 2),
                                apply_delta(t_srow_scol, 0, index + 3),
                            )
                            self.loop(sub, t_srow_scol[0] - 1, oindex + 2)

                start = t_srow_scol
                if last and last[0] == tokenize.STRING:
                    start = self.strings[last[3]]
                    del self.strings[last[3]]
                self.strings[t_erow_ecol] = start
            elif t_type == tokenize.NUMBER:
                self.numbers[t_erow_ecol] = t_srow_scol
            elif t_type == tokenize.NAME and t_string in KEYWORDS:
                self.operators[t_string][t_erow_ecol] = t_srow_scol
            elif t_type == tokenize.NAME and dots == 1:
                self.attributes[t_erow_ecol] = first_dot[2]
                dots = 0
                first_dot = None
            elif t_type == tokenize.NAME and t_string == 'elif':
                self.operators['if'][t_erow_ecol] = t_srow_scol
            elif t_type == tokenize.NAME and t_string in PAST_KEYWORKDS.keys():
                if last and last[1] == PAST_KEYWORKDS[t_string]:
                    combined = "{} {}".format(PAST_KEYWORKDS[t_string], t_string)
                    self.operators[combined][t_erow_ecol] = last[2]
                elif t_string in FUTURE_KEYWORDS:
                    tok[5] = True
                else:
                    self.operators[t_string][t_erow_ecol] = t_srow_scol
            elif t_type == tokenize.NAME and t_string in FUTURE_KEYWORDS:
                tok[5] = True
            elif t_string in SEMI_KEYWORDS:
                self.operators[t_string][t_erow_ecol] = t_srow_scol

            if t_string != '.':
                dots = 0
            if last and last[1] in FUTURE_KEYWORDS and last[5]:
                self.operators[last[1]][last[3]] = last[2]

            if t_type == tokenize.NAME or t_string == 'None':
                self.names[t_string][t_erow_ecol] = t_srow_scol
            if t_type != tokenize.NL:
                last = tok
    

def extract_tokens(code, return_tokens=False):
    # Should I implement a LL 1 parser?
    toc = TokenCollector()
    toc.loop(code)

    if return_tokens:
        return toc.tokens

    result = [
        ElementDict(sorted(toc.parenthesis.items())),
        ElementDict(sorted(toc.sbrackets.items())),
        ElementDict(sorted(toc.brackets.items())),
        ElementDict(sorted(toc.strings.items())),
        ElementDict(sorted(toc.attributes.items())),
        ElementDict(sorted(toc.numbers.items())),
    ]
    operators = {k: ElementDict(sorted(v.items()))
                 for k, v in toc.operators.items()}
    names = {k: ElementDict(sorted(v.items()))
             for k, v in toc.names.items()}
    return result, operators, names
