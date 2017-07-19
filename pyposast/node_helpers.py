# Copyright (c) 2015 Universidade Federal Fluminense (UFF)
# This file is part of PyPosAST.
# Please, consult the license terms in the LICENSE file.

from __future__ import (absolute_import, division, unicode_literals)

from copy import copy

from .constants import WHITESPACE
from .utils import (inc_tuple, dec_tuple, LineCol, position_between,
                    find_in_between)


class NodeWithPosition(object):

    def __init__(self, last, first):
        self.first_line, self.first_col = first
        self.uid = self.last_line, self.last_col = last

    def __repr__(self):
        return (
            "Node("
            "({0.first_line}, {0.first_col}), "
            "({0.last_line}, {0.last_col}), "
            "{0.uid})"
        ).format(self)

def nprint(node):
    d = dir(node)
    print('-----------')
    print('class:', node.__class__)
    # print('dir:', d)
    if 'lineno' in d:
        print('ast:', (node.lineno, node.col_offset))
    if 'first_line' in d:
        print('first last uid:', (node.first_line, node.first_col),
              (node.last_line, node.last_col),
              node.uid)
    if 'op_pos' in d:
        print('op_pos:', node.op_pos)
    print('-----------')


def copy_info(node_to, node_from):
    node_to.first_line = node_from.first_line
    node_to.first_col = node_from.first_col
    node_to.last_line = node_from.last_line
    node_to.last_col = node_from.last_col
    node_to.uid = node_from.uid


def ast_pos(node, bytes_pos_to_utf8):
    bytes_pos = bytes_pos_to_utf8[node.lineno - 1]
    return node.lineno, bytes_pos.get(node.col_offset)


def copy_from_lineno_col_offset(node, identifier, bytes_pos_to_utf8, to=None):
    if to is None:
        to = node
    to.first_line, to.first_col = ast_pos(node, bytes_pos_to_utf8)
    to.last_line = node.lineno
    len_id = len(identifier)
    to.last_col = to.first_col + len_id
    to.uid = (to.last_line, to.last_col)


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


def keyword_followed_by_ids(node, keyword, names, ids, bytes_pos_to_utf8):
    node.uid, first = keyword.find_next(ast_pos(node, bytes_pos_to_utf8))
    node.first_line, node.first_col = first
    last = node.uid
    node.ids_pos = []
    for name in ids:
        last, first = names[name].find_next(last)
        node.ids_pos.append(NodeWithPosition(last, first))

    node.last_line, node.last_col = last


def start_by_keyword(node, keyword, bytes_pos_to_utf8, set_last=True):
    position = ast_pos(node, bytes_pos_to_utf8)
    try:
        node.uid, first = keyword.find_next(position)
        if first != position:
            raise IndexError
    except IndexError:
        node.uid, first = keyword.find_previous(position)
    node.first_line, node.first_col = first
    if set_last:
        node.last_line, node.last_col = node.uid


def update_expr_parenthesis(code, parenthesis, node):
    """Find parenthesis before and after node"""
    position = (node.first_line, node.first_col)
    open_paren, close_paren = find_in_between(position, parenthesis)
    if not open_paren:
        # There is not opening parenthesis
        return
    open_paren = LineCol(code, *open_paren)
    close_paren = LineCol(code, *dec_tuple(close_paren))

    start = LineCol(code, node.first_line, node.first_col)
    end = LineCol(code, node.last_line, node.last_col)
    original_start = copy(start)
    original_end = copy(end)

    start.dec()
    while start > open_paren and not start.bof and start.char() in WHITESPACE:
        start.dec()

    while end < close_paren and not end.eof and end.char() in WHITESPACE:
        end.inc()

    if start == open_paren and end == close_paren:
        end_tuple = inc_tuple(end.tuple())
        node.first_line, node.first_col = start.tuple()
        if node.uid == (node.last_line, node.last_col):
            node.uid = end_tuple
        node.last_line, node.last_col = end_tuple

        update_expr_parenthesis(code, parenthesis, node)

        node.pos_before = NodeWithPosition(
            original_start.tuple(),
            (node.first_line, node.first_col),
        )
        node.pos_inner = NodeWithPosition(
            original_end.tuple(),
            original_start.tuple(),
        )
        node.pos_after = NodeWithPosition(
            (node.last_line, node.last_col),
            original_end.tuple(),
        )


def update_position_between_cursors(code, node, start, end):
    """Update node position according to LineCols"""
    if isinstance(start, LineCol):
        start = start.tuple()
    if isinstance(end, LineCol):
        end = end.tuple()
    start, end = position_between(code, start, end)
    node.first_line, node.first_col = start
    if node.uid == (node.last_line, node.last_col):
        node.uid = end
    (node.last_line, node.last_col) = end


def increment_node_position(code, node):
    """Increment start position and decrement end position
    It is used to remove parenthesis on calls with a single argument"""
    first = (node.first_line, node.first_col)
    last = (node.last_line, node.last_col)
    cursor1, cursor2 = LineCol(code, *first), LineCol(code, *last)
    cursor1.inc()
    cursor2.dec()
    update_position_between_cursors(code, node, cursor1, cursor2)
    if hasattr(node, 'pos_before'):
        before = node.pos_before
        update_position_between_cursors(
            code, before,
            cursor1,
            (before.last_line, before.last_col)
        )
        if (before.last_line, before.last_col) == cursor1.tuple():
            del node.pos_before
    if hasattr(node, 'pos_after'):
        after = node.pos_after
        update_position_between_cursors(
            code, after,
            (after.first_line, after.first_col),
            cursor2,
        )
        if (after.last_line, after.last_col) == cursor2.tuple():
            del node.pos_after
    if hasattr(node, 'pos_inner'):
        if not hasattr(node, 'pos_before') and not hasattr(node, 'pos_after'):
            del node.pos_inner
