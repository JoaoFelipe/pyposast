import ast
import tokenize
import bisect

from collections import OrderedDict, defaultdict
from operator import sub

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


class NodeWithPosition(object):

    def __init__(self, last, first):
        self.first_line, self.first_col = first
        self.uid = self.last_line, self.last_col = last


def extract_tokens(code, return_tokens=False):
    result = [
        parenthesis, sbrackets, strings, attributes, numbers
    ] = StackElement('(', ')'), StackElement('[', ']'), {}, {}, {},
    operators = defaultdict(dict)

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
            parenthesis.check(t_string, t_srow_scol, t_erow_ecol)
            sbrackets.check(t_string, t_srow_scol, t_erow_ecol)
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
        elif t_type == tokenize.NAME and dots == 1:
            attributes[t_erow_ecol] = first_dot[2]
            dots = 0
            first_dot = None
        elif t_type == tokenize.NAME and t_string in ('and', 'or'):
            operators[t_string][t_erow_ecol] = t_srow_scol
        elif t_type == tokenize.NAME and t_string == 'is':
            tok[5] = True
        elif t_type == tokenize.NAME and t_string == 'in':
            if last[1] == 'not':
                operators['not in'][t_erow_ecol] = last[2]
                last[5] = False
            else:
                operators['in'][t_erow_ecol] = t_srow_scol
        elif t_type == tokenize.NAME and t_string == 'not':
            if last[1] == 'is':
                operators['is not'][t_erow_ecol] = last[2]
                last[5] = False
            else:
                tok[5] = True
        if last and last[1] in ('not', 'is') and last[5]:
            operators[last[1]][last[3]] = last[2]

        if t_type != tokenize.NL:
            last = tok

    if return_tokens:
        return tokens

    result = [ElementDict(sorted(x.items())) for x in result]
    operators = {k: ElementDict(sorted(v.items())) for k, v in operators.items()}
    return result, operators


def nprint(node):
    print(dir(node))
    print(node.lineno, node.col_offset)

OPERATORS = {
    ast.And: ('and',),
    ast.Or: ('or',),
    ast.Add: ('+',),
    ast.Sub: ('-',),
    ast.Mult: ('*',),
    ast.Div: ('/',),
    ast.Mod: ('%',),
    ast.Pow: ('**',),
    ast.LShift: ('<<',),
    ast.RShift: ('>>',),
    ast.BitOr: ('|',),
    ast.BitXor: ('^',),
    ast.BitAnd: ('&',),
    ast.FloorDiv: ('//',),
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
}

def copy_info(node_to, node_from):
    node_to.first_line = node_from.first_line
    node_to.first_col = node_from.first_col
    node_to.last_line = node_from.last_line
    node_to.last_col = node_from.last_col
    node_to.uid = node_from.uid

def set_pos(node, first, last):
    node.first_line, node.first_col = first
    node.uid = node.last_line, node.last_col = last

def r_set_pos(node, last, first):
    node.first_line, node.first_col = first
    node.uid = node.last_line, node.last_col = last

def min_first_max_last(node, other):
    node.first_line, node.first_col = min(
        (node.first_line, node.first_col),
        (other.first_line, other.first_col))
    node.last_line, node.last_col = max(
        (node.last_line, node.last_col),
        (other.last_line, other.last_col))

def set_max_position(node):
    node.first_line, node.first_col = float('inf'), float('inf')
    node.last_line, node.last_col = float('-inf'), float('-inf')




class ProvenanceVisitor(ast.NodeVisitor):

    def __init__(self, code, path):
        self.tree = ast.parse(code, path)
        self.code = code
        tokens, self.operators = extract_tokens(code)
        self.parenthesis = tokens[0]
        self.sbrackets = tokens[1]
        self.strings = tokens[2]
        self.attributes = tokens[3]
        self.numbers = tokens[4]
        self.visit(self.tree)

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
        position = (node.first_line, node.first_col)
        node.last_line, node.last_col = self.numbers.find_next(position)[0]
        node.uid = (node.last_line, node.last_col)
        return result

    def visit_Str(self, node):
        result = self.generic_visit(node)
        position = (node.lineno, node.col_offset)
        r_set_pos(node, *self.strings.find_next(position))
        return result

    def visit_Attribute(self, node):
        result = self.generic_visit(node)
        position = (node.value.last_line, node.value.last_col + len(node.attr))
        r_set_pos(node, *self.attributes.find_next(position))
        node.uid = node.first_line, node.first_col
        node.first_line = node.value.first_line
        node.first_col = node.value.first_col
        return result

    def visit_Index(self, node):
        result = self.generic_visit(node)
        copy_info(node, node.value)
        return result

    def visit_Ellipsis(self, node):
        result = self.generic_visit(node)
        if 'lineno' in dir(node):
            """ Python 3 """
            position = (node.lineno, node.col_offset)
            r_set_pos(node, *self.operators['...'].find_next(position))
        return result

    def visit_Slice(self, node):
        result = self.generic_visit(node)
        set_max_position(node)
        node.children = [node.lower, node.upper, node.step]

        for sub_node in node.children:
            if sub_node:
                min_first_max_last(node, sub_node)

        return result


    def process_slice(self, the_slice, previous):
        if isinstance(the_slice, ast.Ellipsis):
            """ Python 2 ellipsis has no location """
            position = (previous.last_line, previous.last_col + 1)
            r_set_pos(the_slice, *self.operators['...'].find_next(position))

        elif isinstance(the_slice, ast.Slice):
            position = (previous.last_line, previous.last_col + 1)
            the_slice.uid = self.operators[':'].find_next(position)[0]
            if not the_slice.lower:
                the_slice.first_line, the_slice.first_col = the_slice.uid
                the_slice.first_col -= 1
            if not the_slice.upper and not the_slice.step:
                the_slice.last_line, the_slice.last_col = the_slice.uid

        elif isinstance(the_slice, ast.ExtSlice):
            set_max_position(the_slice)

            last_dim = previous
            for dim in the_slice.dims:
                self.process_slice(dim, last_dim)
                min_first_max_last(the_slice, dim)
                last_dim = dim

            for previous, dim in pairwise(the_slice.dims):
                self.post_process_slice(previous,
                                        (dim.first_line, dim.first_col))

            the_slice.uid = (the_slice.dims[0].last_line,
                             the_slice.dims[0].last_col + 1)


    def post_process_slice(self, previous, position):
        if isinstance(previous, ast.ExtSlice):
            self.post_process_slice(previous.dims[-1], position)
        if isinstance(previous, ast.Slice) or isinstance(previous, ast.ExtSlice):
            new_position = self.operators[':'].find_previous(position)[0]
            if new_position > (previous.last_line, previous.last_col):
                previous.last_line, previous.last_col = new_position


    def visit_Subscript(self, node):
        result = self.generic_visit(node)
        self.process_slice(node.slice, node.value)
        position = (node.value.last_line, node.value.last_col)
        set_pos(node, *self.sbrackets.find_next(position))
        node.first_line = node.value.first_line
        node.first_col = node.value.first_col
        self.post_process_slice(node.slice, node.uid)
        return result

    def visit_Tuple(self, node):
        result = self.generic_visit(node)
        if not node.elts:
        # nprint(node)
            position = (node.lineno, node.col_offset)
            set_pos(node, *self.parenthesis.find_previous(position))
        else:
            first = node.elts[0]
            position = (first.last_line, first.last_col + 1)
            node.uid = self.operators[','].find_next(position)[1]
            set_max_position(node)
            for elt in node.elts:
                min_first_max_last(node, elt)

        return result

    def visit_List(self, node):
        result = self.generic_visit(node)
        position = (node.lineno, node.col_offset)
        set_pos(node, *self.sbrackets.find_previous(position))
        return result

    def visit_Repr(self, node):
        """ Python 2 """
        result = self.generic_visit(node)
        position = (node.value.last_line, node.value.last_col + 1)
        r_set_pos(node, *self.operators['`'].find_next(position))
        position = (node.value.first_line, node.value.first_col + 1)
        first = self.operators['`'].find_previous(position)[1]
        node.first_line, node.first_col = first
        return result

    def visit_Call(self, node):
        result = self.generic_visit(node)
        copy_info(node, node.func)
        position = (node.last_line, node.last_col)
        last = self.parenthesis.find_next(position)[1]
        node.uid = node.last_line, node.last_col = last
        return result

    def calculate_cmpop(self, node, previous, next_node):
        previous_position = (previous.last_line, previous.last_col - 1)
        position = (next_node.first_line, next_node.first_col + 1)
        possible = []
        for ch in OPERATORS[node.__class__]:
            try:
                pos = self.operators[ch].find_previous(position)
                if previous_position < pos[1] < position:
                    possible.append(pos)
            except KeyError:
                pass

        return NodeWithPosition(
            *min(possible, key=lambda x: tuple(map(sub, position, x[0])))
        )

    def visit_Compare(self, node):
        result = self.generic_visit(node)
        node.op_pos = []
        set_max_position(node)

        min_first_max_last(node, node.left)
        previous = node.left
        for i, comparator in enumerate(node.comparators):
            # Cannot set to the cmpop node as they are singletons
            node.op_pos.append(
                self.calculate_cmpop(node.ops[i], previous, comparator)
            )
            min_first_max_last(node, comparator)
            previous = comparator

        node.uid = node.last_line, node.last_col
        return result
