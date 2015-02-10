import ast
import tokenize
import bisect

from collections import OrderedDict

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO


def extract_tokens(code):
    parenthesis = {}
    strings = {}
    attributes = {}
    stack = []
    last = None
    next_is_attribute = False
    f = StringIO(code)
    for tok in tokenize.generate_tokens(f.readline):
        t_type, t_string, t_srow_scol, t_erow_ecol, t_line = tok
        if t_type == tokenize.OP:
            if t_string == '(':
                stack.append(t_srow_scol)
            elif t_string == ')':
                parenthesis[stack.pop()] = t_srow_scol
            elif t_string == '.':
                next_is_attribute = True
        elif t_type == tokenize.STRING:
            start = t_srow_scol
            if last and last[0] == tokenize.STRING:
                start = strings[last[3]]
                del strings[last[3]]
            strings[t_erow_ecol] = start
        elif t_type == tokenize.NAME and next_is_attribute:
            next_is_attribute = False
            attributes[t_erow_ecol] = last[2]
        if t_type != tokenize.NL:
            last = tok
    parenthesis = OrderedDict(sorted(parenthesis.items()))
    strings = OrderedDict(sorted(strings.items()))
    attributes = OrderedDict(sorted(attributes.items()))
    return parenthesis, strings, attributes


class ProvenanceVisitor(ast.NodeVisitor):

    def __init__(self, code, path):
        self.tree = ast.parse(code, path)
        tokens = extract_tokens(code)
        self.parenthesis = tokens[0]
        self.strings = tokens[1]
        self.attributes = tokens[2]
        self.strings_keys = list(self.strings.keys())
        self.parenthesis_keys = list(self.parenthesis.keys())
        self.attributes_keys = list(self.attributes.keys())
        self.visit(self.tree)

    def visit_Name(self, node):
        result = self.generic_visit(node)
        node.first_line = node.lineno
        node.first_col = node.col_offset
        node.last_line = node.lineno
        node.last_col = node.col_offset + len(node.id)
        node.uid = (node.last_line, node.last_col)
        return result

    def visit_Num(self, node):
        result = self.generic_visit(node)
        node.first_line = node.lineno
        node.first_col = node.col_offset
        node.last_line = node.lineno
        node.last_col = node.col_offset + len(str(node.n))
        node.uid = (node.last_line, node.last_col)
        return result

    def visit_Str(self, node):
        result = self.generic_visit(node)
        position = (node.lineno, node.col_offset)
        ind = bisect.bisect_left(self.strings_keys, position)
        position = node.last_line, node.last_col = self.strings_keys[ind]
        node.first_line, node.first_col = self.strings[position]
        node.uid = (node.last_line, node.last_col)
        return result

    def visit_Attribute(self, node):
        result = self.generic_visit(node)
        node.first_line = node.value.first_line
        node.first_col = node.value.first_col
        position = (node.value.last_line, node.value.last_col + len(node.attr))
        ind = bisect.bisect_left(self.attributes_keys, position)
        position = node.last_line, node.last_col = self.attributes_keys[ind]
        node.uid = self.attributes[position]
        return result
