import ast
import sys
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

def only_python2(fn):
    def decorator(*args, **kwargs):
        if sys.version_info < (3, 0):
            return fn(*args, **kwargs)
        return None
    return decorator

def only_python3(fn):
    def decorator(*args, **kwargs):
        if sys.version_info >= (3, 0):
            return fn(*args, **kwargs)
        return None
    return decorator

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

WHITESPACE = ('\\', '\r', ' ', '\t')
KEYWORDS = ('and', 'or', 'for', 'if', 'lambda', 'None')
COMBINED_KEYWORDS = ('is not', 'yield from', 'not in')
FUTURE_KEYWORDS = ('is', 'yield', 'not')
PAST_KEYWORKDS = {
    'in': 'not',
    'from': 'yield',
    'not': 'is'
}

def extract_tokens(code, return_tokens=False):
    # Should I implement a LL 1 parser?
    stacks = parenthesis, sbrackets, brackets = [
        StackElement(*x) for x in (('(', ')'), ('[', ']'), ('{', '}'))
    ]
    strings, attributes, numbers = {}, {}, {}
    result = [
        parenthesis, sbrackets, brackets, strings, attributes, numbers
    ]
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
        elif t_type == tokenize.NAME and dots == 1:
            attributes[t_erow_ecol] = first_dot[2]
            dots = 0
            first_dot = None
        elif t_type == tokenize.NAME and t_string in KEYWORDS:
            operators[t_string][t_erow_ecol] = t_srow_scol
        elif t_type == tokenize.NAME and t_string in PAST_KEYWORKDS.keys():
            if last[1] == PAST_KEYWORKDS[t_string]:
                combined = "{} {}".format(PAST_KEYWORKDS[t_string], t_string)
                operators[combined][t_erow_ecol] = last[2]
            elif t_string in FUTURE_KEYWORDS:
                tok[5] = True
            else:
                operators[t_string][t_erow_ecol] = t_srow_scol
        elif t_type == tokenize.NAME and t_string in FUTURE_KEYWORDS:
            tok[5] = True

        if last and last[1] in FUTURE_KEYWORDS and last[5]:
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

def copy_from_lineno_col_offset(node, identifier):
    node.first_line, node.first_col = node.lineno, node.col_offset
    node.last_line = node.lineno
    len_id = len(identifier)
    node.last_col = node.col_offset + len_id
    node.uid = (node.last_line, node.last_col)

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

def set_previous_element(node, previous, element_dict):
    position = (previous.first_line, previous.first_col)
    set_pos(node, *element_dict.find_previous(position))

def r_set_previous_element(node, previous, element_dict):
    position = (previous.first_line, previous.first_col)
    r_set_pos(node, *element_dict.find_previous(position))



class LineCol(object):

    def __init__(self, code, line, col):
        self.code = code
        self.line, self.col = line, col
        self.adjust()

    def char(self):
        return self.code[self.line - 1][self.col]

    def inc(self):
        self.col += 1
        if len(self.code[self.line - 1]) == self.col:
            self.col = 0
            self.line += 1

    def dec(self):
        self.col -= 1
        if self.col == -1:
            self.col = len(self.code[self.line - 2]) - 1
            self.line -= 1

    def adjust(self):
        if len(self.code[self.line - 1]) == self.col:
            self.col = 0
            self.line += 1
        if self.col == -1:
            self.col = len(self.code[self.line - 2]) - 1
            self.line -= 1

    @property
    def eof(self):
        return self.line >= len(self.code) and self.col >= len(self.code[-1])

    @property
    def bof(self):
        return self.line <= 0 and self.col <= 0

    def tuple(self):
        return (self.line, self.col)

    def __lt__(self, other):
        return self.tuple() < other.tuple()

    def __eq__(self, other):
        return self.tuple() == other.tuple()

    def __repr__(self):
        return str(self.tuple())


def inc_tuple(tup):
    return (tup[0], tup[1] + 1)


def dec_tuple(tup):
    return (tup[0], tup[1] - 1)


def position_between(code, position1, position2):
    if position1 > position2:
        position1, position2 = position2, position1
    p1, p2 = LineCol(code, *position1), LineCol(code, *position2)
    start = LineCol(code, *position1)
    while start < p2 and start.char() in WHITESPACE:
        start.inc()
    end = LineCol(code, *dec_tuple(position2))
    while end > p1 and end.char() in WHITESPACE:
        end.dec()
    if end > p1:
        end.inc()
    if end == start:
        return position1, position2
    if start > end:
        tup = start.tuple()
        return tup, tup
    return start.tuple(), end.tuple()

def update_expr_parenthesis(code, parenthesis, node):

    position = (node.first_line, node.first_col)
    try:
        p1, p2 = parenthesis.find_previous(position)
    except IndexError:
        return
    if not p1 < position < p2:
        return
    p1, p2 = LineCol(code, *p1), LineCol(code, *dec_tuple(p2))

    start = LineCol(code, node.first_line, node.first_col)
    end = LineCol(code, node.last_line, node.last_col)
    start.dec()

    while start > p1 and not start.bof and start.char() in WHITESPACE:
        start.dec()

    while end < p2 and not end.eof and end.char() in WHITESPACE:
        end.inc()

    if start == p1 and end == p2:
        end_tuple = inc_tuple(end.tuple())
        node.first_line, node.first_col = start.tuple()
        if node.uid == (node.last_line, node.last_col):
            node.uid = end_tuple
        node.last_line, node.last_col = end_tuple

        update_expr_parenthesis(code, parenthesis, node)

def increment_node_position(code, node):
    first = (node.first_line, node.first_col)
    last = (node.last_line, node.last_col)
    p1, p2 = LineCol(code, *first), LineCol(code, *last)
    p1.inc()
    p2.dec()
    start, end = position_between(code, p1.tuple(), p2.tuple())
    node.first_line, node.first_col = start
    if node.uid == (node.last_line, node.last_col):
        node.uid = end
    (node.last_line, node.last_col) = end

def visit_all(fn):
    def decorator(self, node):
        result = self.generic_visit(node)
        fn(self, node)
        return result
    return decorator

def visit_expr(fn):
    def decorator(self, node):
        result = self.generic_visit(node)
        fn(self, node)
        update_expr_parenthesis(self.lcode, self.parenthesis, node)
        return result
    return decorator


class ProvenanceVisitor(ast.NodeVisitor):

    def __init__(self, code, path):
        self.tree = ast.parse(code, path)
        self.code = code
        self.lcode = code.split('\n')
        tokens, self.operators = extract_tokens(code)
        self.parenthesis = tokens[0]
        self.sbrackets = tokens[1]
        self.brackets = tokens[2]
        self.strings = tokens[3]
        self.attributes = tokens[4]
        self.numbers = tokens[5]
        self.visit(self.tree)

    def calculate_infixop(self, node, previous, next_node):
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

    def calculate_unaryop(self, node, next_node):
        position = (next_node.first_line, next_node.first_col + 1)
        possible = []
        for ch in OPERATORS[node.__class__]:
            try:
                pos = self.operators[ch].find_previous(position)
                if pos[1] < position:
                    possible.append(pos)
            except KeyError:
                pass

        return NodeWithPosition(
            *min(possible, key=lambda x: tuple(map(sub, position, x[0])))
        )

    @visit_expr
    def visit_Name(self, node):
        copy_from_lineno_col_offset(node, node.id)

    @visit_expr
    def visit_Num(self, node):
        node.first_line = node.lineno
        node.first_col = node.col_offset
        node.last_line = node.lineno
        position = (node.first_line, node.first_col)
        node.last_line, node.last_col = self.numbers.find_next(position)[0]
        node.uid = (node.last_line, node.last_col)

    @visit_expr
    def visit_Str(self, node):
        position = (node.lineno, node.col_offset)
        r_set_pos(node, *self.strings.find_next(position))

    @visit_expr
    def visit_Attribute(self, node):
        position = (node.value.last_line, node.value.last_col + len(node.attr))
        r_set_pos(node, *self.attributes.find_next(position))
        node.uid = node.first_line, node.first_col
        node.first_line = node.value.first_line
        node.first_col = node.value.first_col

    @visit_all
    def visit_Index(self, node):
        copy_info(node, node.value)

    @only_python3
    @visit_expr
    def visit_Ellipsis(self, node):
        if 'lineno' in dir(node):
            """ Python 3 """
            position = (node.lineno, node.col_offset)
            r_set_pos(node, *self.operators['...'].find_next(position))

    @visit_all
    def visit_Slice(self, node):
        set_max_position(node)
        children = [node.lower, node.upper, node.step]
        node.children = [x for x in children if x]

        if isinstance(node.step, ast.Name) and node.step.id == 'None':
            position = (node.step.first_line, node.step.first_col - 1)
            empty_none = True
            try:
                last, first = self.operators['None'].find_next(position)
                if first == (node.step.first_line, node.step.first_col):
                    empty_none = False
            except KeyError:
                pass
            if empty_none:
                node.step.last_col = node.step.col_offset + 1
                node.step.uid = (node.step.last_line, node.step.last_col)

        for sub_node in node.children:
            min_first_max_last(node, sub_node)

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

    @visit_expr
    def visit_Subscript(self, node):
        self.process_slice(node.slice, node.value)
        position = (node.value.last_line, node.value.last_col)
        set_pos(node, *self.sbrackets.find_next(position))
        node.first_line = node.value.first_line
        node.first_col = node.value.first_col
        self.post_process_slice(node.slice, node.uid)

    @visit_expr
    def visit_Tuple(self, node):
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

    @visit_expr
    def visit_List(self, node):
        position = (node.lineno, node.col_offset)
        set_pos(node, *self.sbrackets.find_previous(position))

    @visit_expr
    def visit_Repr(self, node):
        """ Python 2 """
        position = (node.value.last_line, node.value.last_col + 1)
        r_set_pos(node, *self.operators['`'].find_next(position))
        position = (node.value.first_line, node.value.first_col + 1)
        first = self.operators['`'].find_previous(position)[1]
        node.first_line, node.first_col = first

    @visit_expr
    def visit_Call(self, node):
        copy_info(node, node.func)
        position = (node.last_line, node.last_col)
        last = self.parenthesis.find_next(position)[1]
        node.uid = node.last_line, node.last_col = last
        children = [node.starargs, node.kwargs]
        children += node.args + node.keywords
        children = [x for x in children if x]
        if len(children) == 1 and isinstance(children[0], ast.expr):
            increment_node_position(self.lcode, children[0])

    @visit_expr
    def visit_Compare(self, node):
        node.op_pos = []
        set_max_position(node)

        min_first_max_last(node, node.left)
        previous = node.left
        for i, comparator in enumerate(node.comparators):
            # Cannot set to the cmpop node as they are singletons
            node.op_pos.append(
                self.calculate_infixop(node.ops[i], previous, comparator)
            )
            min_first_max_last(node, comparator)
            previous = comparator

        node.uid = node.last_line, node.last_col

    @visit_expr
    def visit_Yield(self, node):
        copy_info(node, node.value)
        position = (node.lineno, node.col_offset)
        node.uid, first = self.operators['yield'].find_next(position)
        node.first_line, node.first_col = first

    @visit_all
    def visit_comprehension(self, node):
        set_max_position(node)
        r_set_previous_element(node, node.target, self.operators['for'])
        min_first_max_last(node, node.iter)
        for eif in node.ifs:
            min_first_max_last(node, eif)

    @visit_expr
    def visit_GeneratorExp(self, node):
        set_max_position(node)
        min_first_max_last(node, node.elt)
        for generator in node.generators:
            min_first_max_last(node, generator)
        node.uid = node.elt.last_line, node.elt.last_col

    @visit_expr
    def visit_DictComp(self, node):
        set_previous_element(node, node.key, self.brackets)

    @visit_expr
    def visit_SetComp(self, node):
        set_previous_element(node, node.elt, self.brackets)

    @visit_expr
    def visit_ListComp(self, node):
        set_previous_element(node, node.elt, self.sbrackets)

    @visit_expr
    def visit_Set(self, node):
        set_previous_element(node, node.elts[0], self.brackets)

    @visit_expr
    def visit_Dict(self, node):
        position = (node.lineno, node.col_offset + 1)
        set_pos(node, *self.brackets.find_previous(position))

    @visit_expr
    def visit_IfExp(self, node):
        set_max_position(node)
        min_first_max_last(node, node.body)
        min_first_max_last(node, node.orelse)
        position = (node.test.first_line, node.test.first_col + 1)
        node.uid = self.operators['if'].find_previous(position)[0]

    @visit_expr
    def visit_Lambda(self, node):
        copy_info(node, node.body)
        position = (node.body.first_line, node.body.first_col + 1)
        node.uid, before_colon = self.operators[':'].find_previous(position)
        after_lambda, first = self.operators['lambda'].find_previous(position)
        node.first_line, node.first_col = first

        args = node.args
        arg_position = position_between(self.lcode, after_lambda, before_colon)
        args.first_line, args.first_col = arg_position[0]
        args.uid = args.last_line, args.last_col = arg_position[1]

    @visit_all
    def visit_arg(self, node):
        if node.annotation:
            copy_info(node, node.annotation)
        else:
            node.last_line = node.lineno
            node.last_col = node.col_offset + len(node.arg)
        node.first_line, node.first_col = node.lineno, node.col_offset
        node.uid = (node.last_line, node.last_col)

    @visit_all
    def visit_arguments(self, node):
        if 'kwonlyargs' in dir(node):
            """ Python 3 """
            set_max_position(node)
            for arg in node.args:
                min_first_max_last(node, arg)
            if node.vararg:
                min_first_max_last(node, node.vararg)
            for arg in node.kwonlyargs:
                min_first_max_last(node, arg)
            for arg in node.kw_defaults:
                min_first_max_last(node, arg)
            if node.kwarg:
                min_first_max_last(node, node.kwarg)
            for arg in node.defaults:
                min_first_max_last(node, arg)
            node.uid = (node.last_line, node.last_col)

    @visit_expr
    def visit_UnaryOp(self, node):
        # Cannot set to the unaryop node as they are singletons
        node.op_pos = self.calculate_unaryop(node.op, node.operand)
        copy_info(node, node.op_pos)
        min_first_max_last(node, node.operand)

    @visit_expr
    def visit_BinOp(self, node):
        set_max_position(node)
        min_first_max_last(node, node.left)
        min_first_max_last(node, node.right)
        node.op_pos = self.calculate_infixop(node.op, node.left, node.right)
        node.uid = node.op_pos.uid

    @visit_expr
    def visit_BoolOp(self, node):
        node.op_pos = []
        set_max_position(node)

        previous = None
        for value in node.values:
            # Cannot set to the boolop nodes as they are singletons
            if previous:
                node.op_pos.append(
                    self.calculate_infixop(node.op, previous, value)
                )
            min_first_max_last(node, value)
            previous = value

        node.uid = node.last_line, node.last_col

    @visit_expr
    def visit_Starred(self, node):
        """ Python 3 """
        r_set_previous_element(node, node.value, self.operators['*'])
        last = node.value
        node.last_line, node.last_col = last.last_line, last.last_col

    @visit_expr
    def visit_NameConstant(self, node):
        """ Python 3 """
        copy_from_lineno_col_offset(node, str(node.value))

    @visit_expr
    def visit_Bytes(self, node):
        position = (node.lineno, node.col_offset)
        r_set_pos(node, *self.strings.find_next(position))

    @visit_expr
    def visit_YieldFrom(self, node):
        copy_info(node, node.value)
        position = (node.lineno, node.col_offset)
        node.uid, first = self.operators['yield from'].find_next(position)
        node.first_line, node.first_col = first
