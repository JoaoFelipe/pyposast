# Copyright (c) 2016 Universidade Federal Fluminense (UFF)
# This file is part of PyPosAST.
# Please, consult the license terms in the LICENSE file.

from __future__ import (absolute_import, division)


import ast

from copy import copy
from operator import sub
from functools import wraps

from .cross_version import only_python2, only_python3, native_decode_source
from .cross_version import only_python36
from .constants import OPERATORS
from .parser import extract_tokens
from .utils import (pairwise, inc_tuple, dec_tuple, position_between,
                    find_next_parenthesis, find_next_comma, extract_positions,
                    find_next_colon, find_next_equal)
from .node_helpers import (NodeWithPosition, nprint, copy_info, ast_pos,
                           copy_from_lineno_col_offset, set_pos,
                           r_set_pos, min_first_max_last, set_max_position,
                           set_max_position, set_previous_element,
                           r_set_previous_element, update_expr_parenthesis,
                           increment_node_position, keyword_followed_by_ids,
                           start_by_keyword)


def extract_code(lines, node, lstrip="", ljoin="\n", strip=""):
    """Get corresponding text in the code


    Arguments:
    lines -- code splitted by linebreak
    node -- PyPosAST enhanced node


    Keyword Arguments:
    lstrip -- During extraction, strip lines with this arg (default="")
    ljoin -- During extraction, join lines with this arg (default="\n")
    strip -- After extraction, strip all code with this arg (default="")
    """
    first_line, first_col = node.first_line - 1, node.first_col
    last_line, last_col = node.last_line - 1, node.last_col
    if first_line == last_line:
        return lines[first_line][first_col:last_col].strip(strip)

    result = []
    # Add first line
    result.append(lines[first_line][first_col:].strip(lstrip))
    # Add middle lines
    if first_line + 1 != last_line:
        for line in range(first_line + 1, last_line):
            result.append(lines[line].strip(lstrip))
    # Add last line
    result.append(lines[last_line][:last_col].strip(lstrip))
    return ljoin.join(result).strip(strip)


def visit_all(fn):
    @wraps(fn)
    def decorator(self, node, *args, **kwargs):
        result = self.generic_visit(node)
        fn(self, node, *args, **kwargs)
        return result
    return decorator


def visit_expr(fn):
    @wraps(fn)
    def decorator(self, node, *args, **kwargs):
        result = self.generic_visit(node)
        fn(self, node, *args, **kwargs)
        update_expr_parenthesis(self.lcode, self.parenthesis, node)
        return result
    return decorator


visit_stmt = visit_all
visit_mod = visit_all


class LineProvenanceVisitor(ast.NodeVisitor):
    # pylint: disable=invalid-name, missing-docstring
    # pylint: disable=too-many-instance-attributes, too-many-public-methods
    # pylint: disable=no-self-use

    def __init__(self, code, path, mode='exec', tree=None):
        code = native_decode_source(code)
        self.tree = tree or ast.parse(code, path, mode=mode)
        self.code = code
        self.lcode = code.split('\n')
        self.utf8_pos_to_bytes = []
        self.bytes_pos_to_utf8 = []
        if ((only_python2 and isinstance(code, str)) or
                (only_python3 and isinstance(code, bytes))):
            for line in self.lcode:
                same = {j: j for j, c in enumerate(line)}
                self.utf8_pos_to_bytes.append(same)
                self.bytes_pos_to_utf8.append(same)
        else:
            for line in self.lcode:
                utf8, byte = extract_positions(line)
                self.utf8_pos_to_bytes.append(utf8)
                self.bytes_pos_to_utf8.append(byte)

        tokens, self.operators, self.names = extract_tokens(code)
        self.parenthesis = tokens[0]
        self.sbrackets = tokens[1]
        self.brackets = tokens[2]
        self.strings = tokens[3]
        self.attributes = tokens[4]
        self.numbers = tokens[5]
        self.dline = 0
        self.dcol = 0
        self.visit(self.tree)

    def dnode(self, node):
        """Duplicate node and adjust it for deslocated line and column"""
        new_node = copy(node)
        new_node.lineno += self.dline
        new_node.col_offset += self.dcol
        return new_node

    def dposition(self, node, dcol=0):
        """Return deslocated line and column"""
        nnode = self.dnode(node)
        return (nnode.lineno, nnode.col_offset + dcol)

    def calculate_infixop(self, node, previous, next_node):
        """Create new node for infixop"""
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

        if not possible:
            raise ValueError("not a single {} between {} and {}".format(
                OPERATORS[node.__class__], previous_position, position))

        return NodeWithPosition(
            *min(possible, key=lambda x: tuple(map(sub, position, x[0])))
        )

    def calculate_unaryop(self, node, next_node):
        """Create new node for unaryop"""
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

    def uid_something_colon(self, node):
        """ Creates op_pos for node from uid to colon """
        node.op_pos = [
            NodeWithPosition(node.uid, (node.first_line, node.first_col))
        ]
        position = (node.body[0].first_line, node.body[0].first_col)
        last, first = self.operators[':'].find_previous(position)
        node.op_pos.append(NodeWithPosition(last, first))
        return last

    def optional_else(self, node, last):
        """ Create op_pos for optional else """
        if node.orelse:
            min_first_max_last(node, node.orelse[-1])
            if 'else' in self.operators:
                position = (node.orelse[0].first_line, node.orelse[0].first_col)
                _, efirst = self.operators['else'].find_previous(position)
                if efirst and efirst > last:
                    elast, _ = self.operators[':'].find_previous(position)
                    node.op_pos.append(NodeWithPosition(elast, efirst))

    def comma_separated_list(self, node, subnodes):
        """Process comma separated list """
        for item in subnodes:
            position = (item.last_line, item.last_col)
            first, last = find_next_comma(self.lcode, position)
            if first:  # comma exists
                node.op_pos.append(NodeWithPosition(last, first))

    @visit_expr
    def visit_Name(self, node):
        nnode = self.dnode(node)
        copy_from_lineno_col_offset(
            nnode, node.id, self.bytes_pos_to_utf8, to=node
        )

    @visit_expr
    def visit_Num(self, node):
        nnode = self.dnode(node)
        node.first_line, node.first_col = ast_pos(nnode, self.bytes_pos_to_utf8)
        node.last_line = nnode.lineno
        position = (node.first_line, node.first_col)
        node.last_line, node.last_col = self.numbers.find_next(position)[0]
        node.uid = (node.last_line, node.last_col)

    @visit_expr
    def visit_Str(self, node):
        position = self.dposition(node)
        r_set_pos(node, *self.strings.find_next(position))

    @only_python36
    def visit_JoinedStr(self, node):
        position = self.dposition(node)
        last_position = (node.lineno, node.col_offset)
        for value in node.values:
            if isinstance(value, ast.FormattedValue):
                value.bracket = self.brackets.find_next(last_position)
                self.visit(value)
                last_position = (
                    value.bracket[0][0],
                    value.bracket[0][1] + 1,
                )

            else:
                self.visit(value)
        position = self.dposition(node)
        r_set_pos(node, *self.strings.find_next(position))

    @only_python36
    def visit_FormattedValue(self, node):
        set_pos(node, *node.bracket)
        self.dline += node.first_line - 1
        self.dcol += node.first_col
        self.visit(node.value)
        self.dline -= node.first_line - 1
        self.dcol -= node.first_col
        if node.format_spec:
            self.visit(node.format_spec)
        update_expr_parenthesis(self.lcode, self.parenthesis, node)

    @only_python36
    def visit_Constant(self, node):
        """PEP 511: Constants are generated by optimizers"""
        nnode = self.dnode(node)
        node.first_line, node.first_col = ast_pos(nnode, self.bytes_pos_to_utf8)
        node.last_line = node.first_line
        node.last_col = node.first_col + len(repr(node.value))
        node.uid = (node.last_line, node.last_col)

    @visit_expr
    def visit_Attribute(self, node):
        copy_info(node, node.value)
        position = (node.last_line, node.last_col)
        last, _ = self.names[node.attr].find_next(position)
        node.last_line, node.last_col = last
        node.uid, first_dot = self.operators['.'].find_next(position)
        node.op_pos = NodeWithPosition(node.uid, first_dot)

    @visit_all
    def visit_Index(self, node):
        copy_info(node, node.value)

    @only_python3
    @visit_expr
    def visit_Ellipsis(self, node):
        if 'lineno' in dir(node):
            """Python 3"""
            position = self.dposition(node)
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
            except (KeyError, IndexError):
                pass
            if empty_none:
                node.step.last_col = self.dnode(node.step).col_offset + 1
                node.step.uid = (node.step.last_line, node.step.last_col)

        node.op_pos = []
        for sub_node in node.children:
            min_first_max_last(node, sub_node)



    def process_slice(self, the_slice, previous):
        if isinstance(the_slice, ast.Ellipsis):
            """Python 2 ellipsis has no location"""
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
            previous.op_pos = []
            self.comma_separated_list(previous, previous.dims)
        if isinstance(previous, (ast.Slice, ast.ExtSlice)):
            new_position = self.operators[':'].find_previous(position)[0]
            if new_position > (previous.last_line, previous.last_col):
                previous.last_line, previous.last_col = new_position

        if isinstance(previous, ast.Slice):
            if ':' in self.operators:
                start = (previous.first_line, previous.first_col)
                position = inc_tuple((previous.last_line, previous.last_col))
                for _ in range(2):
                    clast, cfirst = self.operators[':'].find_previous(position)
                    if cfirst and cfirst >= start:
                        previous.op_pos.append(NodeWithPosition(clast, cfirst))
                        position = inc_tuple(cfirst)
                    else:
                        break
                previous.op_pos.reverse()

    @visit_expr
    def visit_Subscript(self, node):
        self.process_slice(node.slice, node.value)
        position = (node.value.last_line, node.value.last_col)
        first, last = self.sbrackets.find_next(position)
        set_pos(node, first, last)
        node.op_pos = [
            NodeWithPosition(inc_tuple(first), first),
            NodeWithPosition(last, dec_tuple(last)),
        ]
        node.first_line = node.value.first_line
        node.first_col = node.value.first_col
        self.post_process_slice(node.slice, node.uid)

    @visit_expr
    def visit_Tuple(self, node):
        node.op_pos = []
        if not node.elts:
            position = self.dposition(node, dcol=1)
            set_pos(node, *self.parenthesis.find_previous(position))
        else:
            first = node.elts[0]
            position = (first.last_line, first.last_col + 1)
            last, node.uid = self.operators[','].find_next(position)
            set_max_position(node)
            node.last_line, node.last_col = last
            for elt in node.elts:
                min_first_max_last(node, elt)
                position = (elt.last_line, elt.last_col)
                first, last = find_next_comma(self.lcode, position)
                if first:
                    # comma exists
                    node.op_pos.append(NodeWithPosition(last, first))
                    min_first_max_last(node, node.op_pos[-1])

    @visit_expr
    def visit_List(self, node):
        position = self.dposition(node, dcol=1)
        set_pos(node, *self.sbrackets.find_previous(position))
        node.op_pos = []
        self.comma_separated_list(node, node.elts)

    @visit_expr
    def visit_Repr(self, node):
        """ Python 2 """
        position = (node.value.last_line, node.value.last_col + 1)
        r_set_pos(node, *self.operators['`'].find_next(position))
        position = (node.value.first_line, node.value.first_col + 1)
        first = self.operators['`'].find_previous(position)[1]
        node.first_line, node.first_col = first
        node.op_pos = [
            NodeWithPosition((node.first_line, node.first_col + 1), first),
            NodeWithPosition(node.uid, (node.last_line, node.last_col - 1)),
        ]

    @visit_expr
    def visit_Call(self, node):
        node.op_pos = []
        copy_info(node, node.func)
        position = (node.last_line, node.last_col)
        first, last = self.parenthesis.find_next(position)
        node.op_pos.append(NodeWithPosition(inc_tuple(first), first))
        node.uid = node.last_line, node.last_col = last
        children = []
        if hasattr(node, 'starargs'):  # Python <= 3.4
            children += [['starargs', node.starargs], ['kwargs', node.kwargs]]
        children += [['args', x] for x in node.args]
        children += [['keywords', x] for x in node.keywords]
        children = [x for x in children if x[1] is not None]
        if len(children) == 1 and isinstance(children[0][1], ast.expr):
            increment_node_position(self.lcode, children[0][1])

        for child in children:
            position = (child[1].last_line, child[1].last_col)
            firstc, lastc = find_next_comma(self.lcode, position)
            if firstc:  # comma exists
                child.append(NodeWithPosition(lastc, firstc))
            else:
                child.append(None)

        children.sort(key=lambda x: (x[2] is None, getattr(x[2], 'uid', None)))
        for child in children:
            if child[-1]:
                node.op_pos.append(child[-1])

        node.arg_order = children

        node.op_pos.append(NodeWithPosition(last, dec_tuple(last)))

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
    def visit_Await(self, node):
        start_by_keyword(node, self.operators['await'], self.bytes_pos_to_utf8)
        min_first_max_last(node, node.value)
        node.op_pos = [
            NodeWithPosition(node.uid, (node.first_line, node.first_col))
        ]

    @visit_expr
    def visit_Yield(self, node):
        start_by_keyword(node, self.operators['yield'], self.bytes_pos_to_utf8)
        if node.value:
            min_first_max_last(node, node.value)
        node.op_pos = [
            NodeWithPosition(node.uid, (node.first_line, node.first_col))
        ]

    @visit_all
    def visit_comprehension(self, node):
        set_max_position(node)
        if hasattr(node, 'is_async') and node.is_async:  # async in python 3.6
            r_set_previous_element(node, node.target, self.operators['async'])
            first = node.first_line, node.first_col
            r_set_previous_element(node, node.target, self.operators['for'])
            node.first_line, node.first_col = first
        else:
            r_set_previous_element(node, node.target, self.operators['for'])
        node.op_pos = [
            NodeWithPosition(node.uid, (node.first_line, node.first_col))
        ]
        min_first_max_last(node, node.iter)
        position = (node.iter.first_line, node.iter.first_col)
        last, first = self.operators['in'].find_previous(position)
        node.op_pos.append(NodeWithPosition(last, first))
        for eif in node.ifs:
            min_first_max_last(node, eif)
            position = dec_tuple((eif.first_line, eif.first_col))
            last, first = self.operators['if'].find_next(position)
            node.op_pos.append(NodeWithPosition(last, first))

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
        node.op_pos = []
        self.comma_separated_list(node, node.elts)

    @visit_expr
    def visit_Dict(self, node):
        node.op_pos = []
        position = self.dposition(node, dcol=1)
        set_pos(node, *self.brackets.find_previous(position))
        for key, value in zip(node.keys, node.values):
            position = (key.last_line, key.last_col)
            first, last = find_next_colon(self.lcode, position)
            node.op_pos.append(NodeWithPosition(last, first))

            position = (value.last_line, value.last_col)
            first, last = find_next_comma(self.lcode, position)
            if first:  # comma exists
                node.op_pos.append(NodeWithPosition(last, first))

    @visit_expr
    def visit_IfExp(self, node):
        set_max_position(node)
        min_first_max_last(node, node.body)
        min_first_max_last(node, node.orelse)
        position = (node.test.first_line, node.test.first_col + 1)
        node.uid = self.operators['if'].find_previous(position)[0]
        else_pos = self.operators['else'].find_previous(position)[0]
        node.op_pos = [
            NodeWithPosition(node.uid, (node.uid[0], node.uid[1] - 2)),
            NodeWithPosition(else_pos, (else_pos[0], else_pos[1] - 4))
        ]

    def update_arguments(self, args, previous, after):
        arg_position = position_between(self.lcode, previous, after)
        args.first_line, args.first_col = arg_position[0]
        args.uid = args.last_line, args.last_col = arg_position[1]

    @visit_expr
    def visit_Lambda(self, node):
        copy_info(node, node.body)
        position = inc_tuple((node.body.first_line, node.body.first_col))
        node.uid, before_colon = self.operators[':'].find_previous(position)
        after_lambda, first = self.operators['lambda'].find_previous(position)
        node.first_line, node.first_col = first
        self.update_arguments(node.args, after_lambda, before_colon)
        node.op_pos = [
            NodeWithPosition(after_lambda, first),
            NodeWithPosition(node.uid, before_colon),
        ]

    @visit_all
    def visit_arg(self, node):
        nnode = self.dnode(node)
        node.op_pos = []
        if node.annotation:
            copy_info(node, node.annotation)
            position = (node.first_line, node.first_col)
            last, first = self.operators[':'].find_previous(position)
            node.op_pos.append(NodeWithPosition(last, first))
        else:
            node.last_line = nnode.lineno
            node.last_col = nnode.col_offset + len(node.arg)
        node.first_line, node.first_col = nnode.lineno, nnode.col_offset
        node.uid = (node.last_line, node.last_col)

    def find_next_comma(self, node, sub):
        """Find comma after sub andd add NodeWithPosition in node"""
        position = (sub.last_line, sub.last_col)
        first, last = find_next_comma(self.lcode, position)
        if first:  # comma exists
            node.op_pos.append(NodeWithPosition(last, first))

    @visit_all
    def visit_arguments(self, node):
        node.op_pos = []

        if hasattr(node, 'kwonlyargs'):  # Python 3
            node.vararg_node = node.vararg
            node.kwarg_node = node.kwarg
        else:
            set_max_position(node)
            for arg in node.args:
                min_first_max_last(node, arg)

            node.vararg_node = None
            node.kwarg_node = None
            position = (node.first_line, node.first_col)

            if node.vararg:
                last, first = self.names[node.vararg].find_next(position)
                node.vararg_node = NodeWithPosition(last, first)

            if node.kwarg:
                last, first = self.names[node.kwarg].find_next(position)
                node.kwarg_node = NodeWithPosition(last, first)


        set_max_position(node)
        for arg in node.args:
            min_first_max_last(node, arg)
        for arg in node.defaults:
            min_first_max_last(node, arg)

        # Positional args / defaults
        pos_args = node.args[:-len(node.defaults) or None]
        self.comma_separated_list(node, pos_args)
        for arg, default in zip(node.args[len(pos_args):], node.defaults):
            position = (arg.last_line, arg.last_col)
            first, last = find_next_equal(self.lcode, position)
            node.op_pos.append(NodeWithPosition(last, first))
            self.find_next_comma(node, default)

        # *args
        if node.vararg_node:
            min_first_max_last(node, node.vararg_node)

            position = (node.vararg_node.first_line, node.vararg_node.first_col)
            last, first = self.operators['*'].find_previous(position)
            node.op_pos.append(NodeWithPosition(last, first))
            self.find_next_comma(node, node.vararg_node)

        # **kwargs
        if node.kwarg_node:
            min_first_max_last(node, node.kwarg_node)

            position = (node.kwarg_node.first_line, node.kwarg_node.first_col)
            last, first = self.operators['**'].find_previous(position)
            node.op_pos.append(NodeWithPosition(last, first))
            self.find_next_comma(node, node.kwarg_node)

        if hasattr(node, 'kwonlyargs'):  # Python 3
            if node.kwonlyargs and not node.vararg:
                position = (node.kwonlyargs[0].first_line, node.kwonlyargs[0].first_col)
                last, first = self.operators['*'].find_previous(position)
                node.op_pos.append(NodeWithPosition(last, first))
                self.find_next_comma(node, node.op_pos[-1])

            for arg, default in zip(node.kwonlyargs, node.kw_defaults):
                min_first_max_last(node, arg)
                last_node = arg
                if default:
                    min_first_max_last(node, default)
                    last_node = default
                    position = (arg.last_line, arg.last_col)
                    first, last = find_next_equal(self.lcode, position)
                    node.op_pos.append(NodeWithPosition(last, first))
                self.find_next_comma(node, last_node)

        node.uid = (node.last_line, node.last_col)



    @visit_expr
    def visit_UnaryOp(self, node):
        # Cannot set to the unaryop node as they are singletons
        node.op_pos = [self.calculate_unaryop(node.op, node.operand)]
        copy_info(node, node.op_pos[0])
        min_first_max_last(node, node.operand)

    @visit_expr
    def visit_BinOp(self, node):
        set_max_position(node)
        min_first_max_last(node, node.left)
        min_first_max_last(node, node.right)
        node.op_pos = [self.calculate_infixop(node.op, node.left, node.right)]
        node.uid = node.op_pos[0].uid

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
        position = (node.value.first_line, node.value.first_col + 1)
        r_set_pos(node, *self.operators['*'].find_previous(position))
        last = node.value
        node.last_line, node.last_col = last.last_line, last.last_col
        node.op_pos = [
            NodeWithPosition(node.uid, dec_tuple(node.uid))
        ]

    @visit_expr
    def visit_NameConstant(self, node):
        """ Python 3 """
        nnode = self.dnode(node)
        copy_from_lineno_col_offset(
            nnode, str(node.value), self.bytes_pos_to_utf8, to=node)

    @visit_expr
    def visit_Bytes(self, node):
        position = self.dposition(node)
        r_set_pos(node, *self.strings.find_next(position))

    @visit_expr
    def visit_YieldFrom(self, node):
        copy_info(node, node.value)
        position = self.dposition(node)
        node.uid, first = self.operators['yield from'].find_next(position)
        node.first_line, node.first_col = first
        node.op_pos = [
            NodeWithPosition(node.uid, (node.first_line, node.first_col))
        ]

    @visit_stmt
    def visit_Pass(self, node):
        nnode = self.dnode(node)
        copy_from_lineno_col_offset(
            nnode, 'pass', self.bytes_pos_to_utf8, to=node)

    @visit_stmt
    def visit_Break(self, node):
        nnode = self.dnode(node)
        copy_from_lineno_col_offset(
            node, 'break', self.bytes_pos_to_utf8, to=node)

    @visit_stmt
    def visit_Continue(self, node):
        nnode = self.dnode(node)
        copy_from_lineno_col_offset(
            nnode, 'continue', self.bytes_pos_to_utf8, to=node)

    @visit_stmt
    def visit_Expr(self, node):
        copy_info(node, node.value)

    @visit_stmt
    def visit_Nonlocal(self, node):
        keyword_followed_by_ids(node, self.operators['nonlocal'], self.names,
                                node.names, self.bytes_pos_to_utf8)
        node.op_pos = [
            NodeWithPosition(node.uid, (node.first_line, node.first_col))
        ]
        self.comma_separated_list(node, node.ids_pos)

    @visit_stmt
    def visit_Global(self, node, op='global'):
        keyword_followed_by_ids(node, self.operators['global'], self.names,
                                node.names, self.bytes_pos_to_utf8)
        node.op_pos = [
            NodeWithPosition(node.uid, (node.first_line, node.first_col))
        ]
        self.comma_separated_list(node, node.ids_pos)

    @visit_stmt
    def visit_Exec(self, node):
        copy_info(node, node.body)
        start_by_keyword(node, self.operators['exec'],
                         self.bytes_pos_to_utf8, set_last=False)
        node.op_pos = [
            NodeWithPosition(node.uid, (node.first_line, node.first_col))
        ]

        if node.globals:
            position = self.dposition(node.globals)
            last, first = self.operators['in'].find_previous(position)
            node.op_pos.append(NodeWithPosition(last, first))
            min_first_max_last(node, node.globals)
        if node.locals:
            position = self.dposition(node.locals)
            last, first = self.operators[','].find_previous(position)
            node.op_pos.append(NodeWithPosition(last, first))
            min_first_max_last(node, node.locals)

    def process_alias(self, position, alias):
        alias.op_pos = []
        splitted = alias.name.split('.')
        first = None
        for subname in splitted:
            names = self.names if subname != '*' else self.operators
            last, p1 = names[subname].find_next(position)
            if not first:
                first = p1
        if alias.asname:
            last, _ = self.names[alias.asname].find_next(last)
            alast, afirst = self.operators["as"].find_previous(last)
            alias.op_pos.append(NodeWithPosition(alast, afirst))
        alias.first_line, alias.first_col = first
        alias.uid = alias.last_line, alias.last_col = last
        return last

    @visit_stmt
    def visit_ImportFrom(self, node):
        start_by_keyword(node, self.operators['from'], self.bytes_pos_to_utf8)
        last = node.uid
        last, first = self.operators['import'].find_next(last)
        node.op_pos = [
            NodeWithPosition(node.uid, self.dposition(node)),
            NodeWithPosition(last, first),
        ]
        for alias in node.names:
            last = self.process_alias(last, alias)
        par = find_next_parenthesis(self.lcode, last, self.parenthesis)
        if par:
            last = par
        node.last_line, node.last_col = last

    @visit_stmt
    def visit_Import(self, node):
        start_by_keyword(node, self.operators['import'],
                         self.bytes_pos_to_utf8)
        node.op_pos = [
            NodeWithPosition(node.uid, self.dposition(node)),
        ]
        last = node.uid
        for alias in node.names:
            last = self.process_alias(last, alias)
        node.last_line, node.last_col = last

    @visit_stmt
    def visit_Assert(self, node):
        copy_info(node, node.test)
        start_by_keyword(node, self.operators['assert'],
                         self.bytes_pos_to_utf8, set_last=False)
        node.op_pos = [
            NodeWithPosition(node.uid, self.dposition(node)),
        ]
        if node.msg:
            min_first_max_last(node, node.msg)
            position = self.dposition(node.msg)
            last, first = self.operators[','].find_previous(position)
            node.op_pos.append(NodeWithPosition(last, first))

    @visit_stmt
    def visit_TryFinally(self, node):
        start_by_keyword(node, self.operators['try'], self.bytes_pos_to_utf8)
        min_first_max_last(node, node.finalbody[-1])
        position = node.uid
        last, _ = self.operators[':'].find_next(position)
        body = node.body
        if len(body) == 1 and isinstance(body[0], ast.TryExcept):
            node.skip_try = True
            node.op_pos = []
        else:
            node.op_pos = [
                NodeWithPosition(last, self.dposition(node)),
            ]
        position = self.dposition(node.finalbody[0])
        last, _ = self.operators[':'].find_previous(position)
        _, first = self.operators['finally'].find_previous(position)
        node.op_pos.append(NodeWithPosition(last, first))

    @visit_stmt
    def visit_TryExcept(self, node):
        start_by_keyword(node, self.operators['try'], self.bytes_pos_to_utf8)
        position = node.uid
        last, _ = self.operators[':'].find_next(position)
        node.op_pos = [
            NodeWithPosition(last, self.dposition(node)),
        ]
        last_body = node.body
        for handler in node.handlers:
            min_first_max_last(node, handler)
        if node.orelse:
            min_first_max_last(node, node.orelse[-1])
            position = self.dposition(node.orelse[0])
            last, _ = self.operators[':'].find_previous(position)
            _, first = self.operators['else'].find_previous(position)
            node.op_pos.append(NodeWithPosition(last, first))

    @visit_all
    def visit_ExceptHandler(self, node):
        start_by_keyword(node, self.operators['except'],
                         self.bytes_pos_to_utf8)
        min_first_max_last(node, node.body[-1])
        self.uid_something_colon(node)

        node.name_node = node.name
        node_position = (node.first_line, node.first_col)
        if only_python3 and node.name:
            last, first = self.names[node.name].find_next(node_position)
            node.name_node = NodeWithPosition(last, first)

        if node.name_node:
            position = (node.name_node.first_line, node.name_node.first_col)
            first = None
            if 'as' in self.operators:
                last, first = self.operators["as"].find_previous(position)
            if not first:
                last, first = self.operators[","].find_previous(position)
            if first and first > node_position:
                node.op_pos.insert(1, NodeWithPosition(last, first))


    @visit_stmt
    def visit_Try(self, node):
        start_by_keyword(node, self.operators['try'], self.bytes_pos_to_utf8)
        position = node.uid
        last, _ = self.operators[':'].find_next(position)
        node.op_pos = [
            NodeWithPosition(last, self.dposition(node)),
        ]
        last_body = node.body
        for handler in node.handlers:
            min_first_max_last(node, handler)
        if node.orelse:
            min_first_max_last(node, node.orelse[-1])
            position = self.dposition(node.orelse[0])
            last, _ = self.operators[':'].find_previous(position)
            _, first = self.operators['else'].find_previous(position)
            node.op_pos.append(NodeWithPosition(last, first))
        if node.finalbody:
            min_first_max_last(node, node.finalbody[-1])
            position = self.dposition(node.finalbody[0])
            last, _ = self.operators[':'].find_previous(position)
            _, first = self.operators['finally'].find_previous(position)
            node.op_pos.append(NodeWithPosition(last, first))

    @visit_stmt
    def visit_Raise(self, node):
        start_by_keyword(node, self.operators['raise'], self.bytes_pos_to_utf8)
        node.op_pos = [
            NodeWithPosition(node.uid, self.dposition(node)),
        ]
        if 'type' in dir(node):  # Python 2
            children = [node.type, node.inst, node.tback]
            for child in children:
                if not child:
                    continue
                min_first_max_last(node, child)
                position = (child.last_line, child.last_col)
                first, last = find_next_comma(self.lcode, position)
                if first: # comma exists
                    node.op_pos.append(NodeWithPosition(last, first))

        else:  # Python 3
            children = [node.exc, node.cause]
            for child in children:
                if not child:
                    continue
                min_first_max_last(node, child)
            if node.cause:
                position = self.dposition(node.cause)
                last, first = self.operators['from'].find_previous(position)
                node.op_pos.append(NodeWithPosition(last, first))

    @visit_stmt
    def visit_With(self, node, keyword='with'):
        start_by_keyword(node, self.operators[keyword], self.bytes_pos_to_utf8)
        first = node.first_line, node.first_col
        start_by_keyword(node, self.operators['with'], self.bytes_pos_to_utf8)
        node.first_line, node.first_col = first
        min_first_max_last(node, node.body[-1])
        node.op_pos = [
            NodeWithPosition(node.uid, (node.first_line, node.first_col))
        ]
        skip_colon = False
        if hasattr(node, 'optional_vars'):  # Python 2
            last_node = node.context_expr
            if node.optional_vars:
                var = node.optional_vars
                position = (var.first_line, var.first_col)
                last, first = self.operators['as'].find_previous(position)
                node.op_pos.append(NodeWithPosition(last, first))
                last_node = var
            if len(node.body) == 1 and isinstance(node.body[0], ast.With):
                position = (last_node.last_line, last_node.last_col)
                last, first = self.operators[','].find_next(position)
                if first:
                    node.body[0].op_pos[0] = NodeWithPosition(last, first)
                skip_colon = True
        else:
            self.comma_separated_list(node, node.items)

        if not skip_colon:
            position = (node.body[0].first_line, node.body[0].first_col)
            last, first = self.operators[':'].find_previous(position)
            node.op_pos.append(NodeWithPosition(last, first))

    @visit_stmt
    def visit_AsyncWith(self, node):
        """ Python 3.5 """
        self.visit_With(node, keyword='async')

    @visit_all
    def visit_withitem(self, node):
        copy_info(node, node.context_expr)
        node.op_pos = []
        if node.optional_vars:
            min_first_max_last(node, node.optional_vars)
            var = node.optional_vars
            position = (var.first_line, var.first_col)
            last, first = self.operators['as'].find_previous(position)
            node.op_pos.append(NodeWithPosition(last, first))


    @visit_stmt
    def visit_If(self, node):
        start_by_keyword(node, self.operators['if'], self.bytes_pos_to_utf8)
        min_first_max_last(node, node.body[-1])
        last = self.uid_something_colon(node)
        self.optional_else(node, last)

    @visit_stmt
    def visit_While(self, node):
        start_by_keyword(node, self.operators['while'], self.bytes_pos_to_utf8)
        min_first_max_last(node, node.body[-1])
        last = self.uid_something_colon(node)
        self.optional_else(node, last)

    @visit_stmt
    def visit_For(self, node, keyword='for'):
        start_by_keyword(node, self.operators[keyword], self.bytes_pos_to_utf8)
        first = node.first_line, node.first_col
        start_by_keyword(node, self.operators['for'], self.bytes_pos_to_utf8)
        node.first_line, node.first_col = first
        min_first_max_last(node, node.body[-1])
        last = self.uid_something_colon(node)
        position = (node.iter.first_line, node.iter.first_col)
        last, first = self.operators['in'].find_previous(position)
        node.op_pos.insert(1, NodeWithPosition(last, first))
        self.optional_else(node, last)

    @visit_stmt
    def visit_AsyncFor(self, node):
        """ Python 3.5 """
        self.visit_For(node, keyword='async')


    @visit_stmt
    def visit_Print(self, node):
        """ Python 2 """
        start_by_keyword(node, self.operators['print'], self.bytes_pos_to_utf8)
        node.op_pos = [
            NodeWithPosition(node.uid, (node.first_line, node.first_col))
        ]
        subnodes = []
        if node.dest:
            min_first_max_last(node, node.dest)
            position = (node.dest.first_line, node.dest.first_col)
            last, first = self.operators['>>'].find_previous(position)
            node.op_pos.append(NodeWithPosition(last, first))
            subnodes.append(node.dest)
        if node.values:
            min_first_max_last(node, node.values[-1])
            subnodes.extend(node.values)

        self.comma_separated_list(node, subnodes)

    @visit_stmt
    def visit_AugAssign(self, node):
        set_max_position(node)
        min_first_max_last(node, node.target)
        min_first_max_last(node, node.value)
        node.op_pos = self.calculate_infixop(node.op, node.target, node.value)
        node.uid = node.op_pos.uid

    @visit_stmt
    def visit_AnnAssign(self, node):
        set_max_position(node)
        min_first_max_last(node, node.target)
        min_first_max_last(node, node.annotation)
        node.op_pos = []
        node.op_pos.append(
            self.calculate_infixop(node, node.target, node.annotation)
        )
        if node.value:
            min_first_max_last(node, node.value)
            node.op_pos.append(
                self.calculate_infixop(node, node.annotation, node.value)
            )

        node.uid = node.op_pos[0].uid

    @visit_stmt
    def visit_Assign(self, node):
        node.op_pos = []
        set_max_position(node)

        min_first_max_last(node, node.value)
        last = node.value
        for i, target in reversed(list(enumerate(node.targets))):
            node.op_pos.append(
                self.calculate_infixop(node, target, last)
            )
            min_first_max_last(node, target)
            last = target
        node.op_pos = list(reversed(node.op_pos))

        node.uid = node.last_line, node.last_col

    @visit_stmt
    def visit_Delete(self, node):
        start_by_keyword(node, self.operators['del'], self.bytes_pos_to_utf8)
        for target in node.targets:
            min_first_max_last(node, target)

        node.op_pos = [
            NodeWithPosition(node.uid, (node.first_line, node.first_col))
        ]
        self.comma_separated_list(node, node.targets)

    @visit_stmt
    def visit_Return(self, node):
        start_by_keyword(node, self.operators['return'],
                         self.bytes_pos_to_utf8)
        node.op_pos = [
            NodeWithPosition(node.uid, (node.first_line, node.first_col))
        ]
        if node.value:
            min_first_max_last(node, node.value)

    def adjust_decorator(self, node, dec):
        position = dec.first_line, dec.first_col
        if (node.first_line, node.first_col) == position:
            _, first = self.operators['@'].find_previous(position)
            node.first_line, node.first_col = first

    @visit_stmt
    def visit_ClassDef(self, node):
        start_by_keyword(node, self.operators['class'], self.bytes_pos_to_utf8)
        self.uid_something_colon(node)
        for dec in node.decorator_list:
            min_first_max_last(node, dec)
            self.adjust_decorator(node, dec)

        min_first_max_last(node, node.body[-1])

    @visit_all
    def visit_keyword(self, node):
        copy_info(node, node.value)
        node.op_pos = []
        position = (node.first_line, node.first_col + 1)
        if node.arg:
            node.uid, first = self.operators['='].find_previous(position)
            node.op_pos.append(NodeWithPosition(node.uid, first))
            _, first = self.names[node.arg].find_previous(first)
        else:
            node.uid, first = self.operators['**'].find_previous(position)
            node.op_pos.append(NodeWithPosition(node.uid, first))
        node.first_line, node.first_col = first

    @visit_stmt
    def visit_FunctionDef(self, node, keyword='def'):
        lineno, col_offset = node.lineno, node.col_offset
        for dec in node.decorator_list:
            node.lineno = max(node.lineno, dec.last_line + 1)
        start_by_keyword(node, self.operators[keyword], self.bytes_pos_to_utf8)
        first = node.first_line, node.first_col
        start_by_keyword(node, self.operators['def'], self.bytes_pos_to_utf8)
        node.first_line, node.first_col = first
        self.uid_something_colon(node)
        previous, last = self.parenthesis.find_next(node.uid)
        self.update_arguments(node.args, inc_tuple(previous), dec_tuple(last))

        for dec in node.decorator_list:
            min_first_max_last(node, dec)
            self.adjust_decorator(node, dec)

        min_first_max_last(node, node.body[-1])
        node.lineno = lineno

    @visit_stmt
    def visit_AsyncFunctionDef(self, node):
        """ Python 3.5 """
        self.visit_FunctionDef(node, keyword='async')

    @visit_mod
    def visit_Module(self, node):
        set_max_position(node)

        for stmt in node.body:
            min_first_max_last(node, stmt)

        if node.first_line == float('inf'):
            node.first_line, node.first_col = 0, 0
            node.last_line, node.last_col = 0, 0

        node.uid = node.last_line, node.last_col

    @visit_mod
    def visit_Interactive(self, node):
        self.visit_Module(node)

    @visit_mod
    def visit_Expression(self, node):
        copy_info(node, node.body)
