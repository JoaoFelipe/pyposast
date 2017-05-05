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
                    find_next_parenthesis, extract_positions)
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

    def __init__(self, code, path, mode='exec', tree=None):
        code = native_decode_source(code)
        self.tree = tree or ast.parse(code, path, mode=mode)
        self.code = code
        self.lcode = code.split('\n')
        self.utf8_pos_to_bytes = []
        self.bytes_pos_to_utf8 = []
        if ((only_python2 and isinstance(code, str)) or
                (only_python3 and isinstance(code, bytes))):
            for i, line in enumerate(self.lcode):
                same = {j: j for j, c in enumerate(line)}
                self.utf8_pos_to_bytes.append(same)
                self.bytes_pos_to_utf8.append(same)
        else:
            for i, line in enumerate(self.lcode):
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
        new_node = copy(node)
        new_node.lineno += self.dline
        new_node.col_offset += self.dcol
        return new_node

    def dposition(self, node, dcol=0):
        nnode = self.dnode(node)
        return (nnode.lineno, nnode.col_offset + dcol)

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

        if not possible:
            raise ValueError("not a single {} between {} and {}".format(
                OPERATORS[node.__class__], previous_position, position))

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
        node.uid, _ = self.operators['.'].find_next(position)

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
            position = self.dposition(node, dcol=1)
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
        position = self.dposition(node, dcol=1)
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
        children = []
        if hasattr(node, 'starargs'):
            """ Python <= 3.4 """
            children += [node.starargs, node.kwargs]
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
    def visit_Await(self, node):
        start_by_keyword(node, self.operators['await'], self.bytes_pos_to_utf8)
        min_first_max_last(node, node.value)

    @visit_expr
    def visit_Yield(self, node):
        start_by_keyword(node, self.operators['yield'], self.bytes_pos_to_utf8)
        if node.value:
            min_first_max_last(node, node.value)

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
        position = self.dposition(node, dcol=1)
        set_pos(node, *self.brackets.find_previous(position))

    @visit_expr
    def visit_IfExp(self, node):
        set_max_position(node)
        min_first_max_last(node, node.body)
        min_first_max_last(node, node.orelse)
        position = (node.test.first_line, node.test.first_col + 1)
        node.uid = self.operators['if'].find_previous(position)[0]

    def update_arguments(self, args, previous, after):
        arg_position = position_between(self.lcode, previous, after)
        args.first_line, args.first_col = arg_position[0]
        args.uid = args.last_line, args.last_col = arg_position[1]

    @visit_expr
    def visit_Lambda(self, node):
        copy_info(node, node.body)
        position = (node.body.first_line, node.body.first_col + 1)
        node.uid, before_colon = self.operators[':'].find_previous(position)
        after_lambda, first = self.operators['lambda'].find_previous(position)
        node.first_line, node.first_col = first
        self.update_arguments(node.args, after_lambda, before_colon)

    @visit_all
    def visit_arg(self, node):
        nnode = self.dnode(node)
        if node.annotation:
            copy_info(node, node.annotation)
        else:
            node.last_line = nnode.lineno
            node.last_col = nnode.col_offset + len(node.arg)
        node.first_line, node.first_col = nnode.lineno, nnode.col_offset
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
                if arg:
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
        position = (node.value.first_line, node.value.first_col + 1)
        r_set_pos(node, *self.operators['*'].find_previous(position))
        last = node.value
        node.last_line, node.last_col = last.last_line, last.last_col

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

    @visit_stmt
    def visit_Global(self, node):
        keyword_followed_by_ids(node, self.operators['global'], self.names,
                                node.names, self.bytes_pos_to_utf8)

    @visit_stmt
    def visit_Exec(self, node):
        copy_info(node, node.body)
        start_by_keyword(node, self.operators['exec'],
                         self.bytes_pos_to_utf8, set_last=False)
        if node.globals:
            min_first_max_last(node, node.globals)
        if node.locals:
            min_first_max_last(node, node.locals)

    def process_alias(self, position, alias):
        splitted = alias.name.split('.')
        first = None
        for subname in splitted:
            names = self.names if subname != '*' else self.operators
            last, p1 = names[subname].find_next(position)
            if not first:
                first = p1
        if alias.asname:
            last, _ = self.names[alias.asname].find_next(last)
        alias.first_line, alias.first_col = first
        alias.uid = alias.last_line, alias.last_col = last
        return last

    @visit_stmt
    def visit_ImportFrom(self, node):
        start_by_keyword(node, self.operators['from'], self.bytes_pos_to_utf8)
        last = node.uid
        last, _ = self.operators['import'].find_next(last)
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
        last = node.uid
        for alias in node.names:
            last = self.process_alias(last, alias)
        node.last_line, node.last_col = last

    @visit_stmt
    def visit_Assert(self, node):
        copy_info(node, node.test)
        if node.msg:
            min_first_max_last(node, node.msg)
        start_by_keyword(node, self.operators['assert'],
                         self.bytes_pos_to_utf8, set_last=False)

    @visit_stmt
    def visit_TryFinally(self, node):
        start_by_keyword(node, self.operators['try'], self.bytes_pos_to_utf8)
        min_first_max_last(node, node.finalbody[-1])

    @visit_stmt
    def visit_TryExcept(self, node):
        start_by_keyword(node, self.operators['try'], self.bytes_pos_to_utf8)
        if node.orelse:
            min_first_max_last(node, node.orelse[-1])
        for handler in node.handlers:
            min_first_max_last(node, handler)

    @visit_all
    def visit_ExceptHandler(self, node):
        start_by_keyword(node, self.operators['except'],
                         self.bytes_pos_to_utf8)
        min_first_max_last(node, node.body[-1])

    @visit_stmt
    def visit_Try(self, node):
        start_by_keyword(node, self.operators['try'], self.bytes_pos_to_utf8)
        if node.orelse:
            min_first_max_last(node, node.orelse[-1])
        for handler in node.handlers:
            min_first_max_last(node, handler)
        if node.finalbody:
            min_first_max_last(node, node.finalbody[-1])

    @visit_stmt
    def visit_Raise(self, node):
        start_by_keyword(node, self.operators['raise'], self.bytes_pos_to_utf8)
        if 'type' in dir(node):
            """ Python 2 """
            children = [node.type, node.inst, node.tback]
        else:
            """ Python 3 """
            children = [node.exc, node.cause]
        children = [x for x in children if x]
        for child in children:
            min_first_max_last(node, child)

    @visit_stmt
    def visit_With(self, node, keyword='with'):
        start_by_keyword(node, self.operators[keyword], self.bytes_pos_to_utf8)
        min_first_max_last(node, node.body[-1])

    @visit_stmt
    def visit_AsyncWith(self, node):
        """ Python 3.5 """
        self.visit_With(node, keyword='async')

    @visit_all
    def visit_withitem(self, node):
        copy_info(node, node.context_expr)
        if node.optional_vars:
            min_first_max_last(node, node.optional_vars)

    @visit_stmt
    def visit_If(self, node):
        start_by_keyword(node, self.operators['if'], self.bytes_pos_to_utf8)
        min_first_max_last(node, node.body[-1])
        if node.orelse:
            min_first_max_last(node, node.orelse[-1])

    @visit_stmt
    def visit_While(self, node):
        start_by_keyword(node, self.operators['while'], self.bytes_pos_to_utf8)
        min_first_max_last(node, node.body[-1])
        if node.orelse:
            min_first_max_last(node, node.orelse[-1])

    @visit_stmt
    def visit_For(self, node, keyword='for'):
        start_by_keyword(node, self.operators[keyword], self.bytes_pos_to_utf8)
        min_first_max_last(node, node.body[-1])
        if node.orelse:
            min_first_max_last(node, node.orelse[-1])

    @visit_stmt
    def visit_AsyncFor(self, node):
        """ Python 3.5 """
        self.visit_For(node, keyword='async')

    @visit_stmt
    def visit_Print(self, node):
        """ Python 2 """
        start_by_keyword(node, self.operators['print'], self.bytes_pos_to_utf8)
        if node.dest:
            min_first_max_last(node, node.dest)
        if node.values:
            min_first_max_last(node, node.values[-1])

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

    @visit_stmt
    def visit_Return(self, node):
        start_by_keyword(node, self.operators['return'],
                         self.bytes_pos_to_utf8)
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

        for dec in node.decorator_list:
            min_first_max_last(node, dec)
            self.adjust_decorator(node, dec)

        min_first_max_last(node, node.body[-1])

    @visit_all
    def visit_keyword(self, node):
        copy_info(node, node.value)
        position = (node.first_line, node.first_col + 1)
        if node.arg:
            node.uid, first = self.operators['='].find_previous(position)
            _, first = self.names[node.arg].find_previous(first)
        else:
            node.uid, first = self.operators['**'].find_previous(position)
        node.first_line, node.first_col = first

    @visit_stmt
    def visit_FunctionDef(self, node, keyword='def'):
        start_by_keyword(node, self.operators[keyword], self.bytes_pos_to_utf8)
        previous, last = self.parenthesis.find_next(node.uid)
        self.update_arguments(node.args, inc_tuple(previous), dec_tuple(last))

        for dec in node.decorator_list:
            min_first_max_last(node, dec)
            self.adjust_decorator(node, dec)

        min_first_max_last(node, node.body[-1])

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
