import ast
import tokenize
import bisect

from collections import OrderedDict

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO


def pairwise(iterable):
    it = iter(iterable)
    a = next(it)

    for b in it:
        yield (a, b)
        a = b


def extract_tokens(code):
    parenthesis = {}
    sbrackets = {}
    strings = {}
    attributes = {}
    ellipsis = {}
    colons = {}

    parenthesis_stack = []
    sbrackets_stack = []
    last = None

    dots = 0 # number of dots
    first_dot = None

    f = StringIO(code)
    for tok in tokenize.generate_tokens(f.readline):
        t_type, t_string, t_srow_scol, t_erow_ecol, t_line = tok
        if t_type == tokenize.OP:
            if t_string == '(':
                parenthesis_stack.append(t_srow_scol)
            elif t_string == ')':
                parenthesis[parenthesis_stack.pop()] = t_erow_ecol
            if t_string == '[':
                sbrackets_stack.append(t_srow_scol)
            elif t_string == ']':
                sbrackets[sbrackets_stack.pop()] = t_erow_ecol
            elif t_string == '.':
                if not dots:
                    first_dot = tok
                dots += 1
                if dots == 3: # Python 2
                    ellipsis[t_erow_ecol] = first_dot[2]
                    dots = 0
                    first_dot = None
            elif t_string == '...': # Python 3
                ellipsis[t_erow_ecol] = t_srow_scol
            elif t_string == ':':
                colons[t_erow_ecol] = t_srow_scol

        elif t_type == tokenize.STRING:
            start = t_srow_scol
            if last and last[0] == tokenize.STRING:
                start = strings[last[3]]
                del strings[last[3]]
            strings[t_erow_ecol] = start
        elif t_type == tokenize.NAME and dots == 1:
            attributes[t_erow_ecol] = first_dot[2]
            dots = 0
            first_dot = None
        if t_type != tokenize.NL:
            last = tok
    parenthesis = OrderedDict(sorted(parenthesis.items()))
    sbrackets = OrderedDict(sorted(sbrackets.items()))
    strings = OrderedDict(sorted(strings.items()))
    attributes = OrderedDict(sorted(attributes.items()))
    ellipsis = OrderedDict(sorted(ellipsis.items()))
    colons = OrderedDict(sorted(colons.items()))
    return parenthesis, sbrackets, strings, attributes, ellipsis, colons


def nprint(node):
    print(dir(node))
    print(node.lineno, node.col_offset)

class ProvenanceVisitor(ast.NodeVisitor):

    def __init__(self, code, path):
        self.tree = ast.parse(code, path)
        tokens = extract_tokens(code)
        self.parenthesis = tokens[0]
        self.sbrackets = tokens[1]
        self.strings = tokens[2]
        self.attributes = tokens[3]
        self.ellipsis = tokens[4]
        self.colons = tokens[5]
        self.parenthesis_keys = list(self.parenthesis.keys())
        self.sbrackets_keys = list(self.sbrackets.keys())
        self.strings_keys = list(self.strings.keys())
        self.attributes_keys = list(self.attributes.keys())
        self.ellipsis_keys = list(self.ellipsis.keys())
        self.colons_keys = list(self.colons.keys())
        self.visit(self.tree)

    def copy_info(self, node_to, node_from):
        node_to.first_line = node_from.first_line
        node_to.first_col = node_from.first_col
        node_to.last_line = node_from.last_line
        node_to.last_col = node_from.last_col
        node_to.uid = node_from.uid

    def set_max_position(self, node):
        node.first_line, node.first_col = float('inf'), float('inf')
        node.last_line, node.last_col = float('-inf'), float('-inf')

    def visit_Name(self, node):
        result = self.generic_visit(node)
        node.first_line = node.lineno
        node.first_col = node.col_offset
        node.last_line = node.lineno
        len_id = len(node.id) if node.id != 'None' else 1
        node.last_col = node.col_offset + len_id
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

    def visit_Index(self, node):
        result = self.generic_visit(node)
        self.copy_info(node, node.value)
        return result

    def visit_Ellipsis(self, node):
        result = self.generic_visit(node)
        if 'lineno' in dir(node):
            """ Python 3 """
            position = (node.lineno, node.col_offset)
            ind = bisect.bisect_left(self.ellipsis_keys, position)
            node.last_line, node.last_col = self.ellipsis_keys[ind]
            node.uid = (node.last_line, node.last_col)
            node.first_line, node.first_col = self.ellipsis[
                node.uid
            ]
        return result

    def visit_Slice(self, node):
        result = self.generic_visit(node)
        self.set_max_position(node)
        node.children = [node.lower, node.upper, node.step]

        for sub_node in node.children:
            if sub_node:
                node.first_line, node.first_col = min(
                    (node.first_line, node.first_col),
                    (sub_node.first_line, sub_node.first_col))
                node.last_line, node.last_col = max(
                    (node.last_line, node.last_col),
                    (sub_node.last_line, sub_node.last_col))


        return result


    def process_slice(self, the_slice, previous):
        if isinstance(the_slice, ast.Ellipsis):
            """ Python 2 ellipsis has no location """
            position = (previous.last_line, previous.last_col + 1)
            ind = bisect.bisect_left(self.ellipsis_keys, position)
            the_slice.last_line, the_slice.last_col = self.ellipsis_keys[ind]
            the_slice.uid = (the_slice.last_line, the_slice.last_col)
            the_slice.first_line, the_slice.first_col = self.ellipsis[
                the_slice.uid
            ]
        elif isinstance(the_slice, ast.Slice):
            position = (previous.last_line, previous.last_col + 1)
            ind = bisect.bisect_left(self.colons_keys, position)
            the_slice.uid = self.colons_keys[ind]
            if not the_slice.lower:
                the_slice.first_line, the_slice.first_col = the_slice.uid
                the_slice.first_col -= 1
            if not the_slice.upper and not the_slice.step:
                the_slice.last_line, the_slice.last_col = the_slice.uid
        elif isinstance(the_slice, ast.ExtSlice):
            self.set_max_position(the_slice)

            last_dim = previous
            for dim in the_slice.dims:
                self.process_slice(dim, last_dim)
                last_dim = dim

                the_slice.first_line, the_slice.first_col = min(
                    (the_slice.first_line, the_slice.first_col),
                    (dim.first_line, dim.first_col))
                the_slice.last_line, the_slice.last_col = max(
                    (the_slice.last_line, the_slice.last_col),
                    (dim.last_line, dim.last_col))

            for previous, dim in pairwise(the_slice.dims):
                self.post_process_slice(previous,
                                        (dim.first_line, dim.first_col))

            the_slice.uid = (the_slice.dims[0].last_line,
                             the_slice.dims[0].last_col + 1)


    def post_process_slice(self, previous, position):
        if isinstance(previous, ast.ExtSlice):
            self.post_process_slice(previous.dims[-1], position)
        if isinstance(previous, ast.Slice) or isinstance(previous, ast.ExtSlice):
            ind = bisect.bisect_left(self.colons_keys, position) - 1
            position = self.colons_keys[ind]
            if position > (previous.last_line, previous.last_col):
                previous.last_line, previous.last_col = position


    def visit_Subscript(self, node):
        result = self.generic_visit(node)
        self.process_slice(node.slice, node.value)
        position = (node.value.last_line, node.value.last_col)
        ind = bisect.bisect_left(self.sbrackets_keys, position)
        node.first_line = node.value.first_line
        node.first_col = node.value.first_col
        position = self.sbrackets_keys[ind]
        node.last_line, node.last_col = self.sbrackets[position]
        node.uid = (node.last_line, node.last_col)
        self.post_process_slice(node.slice, node.uid)
        return result
