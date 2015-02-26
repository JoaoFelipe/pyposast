from __future__ import (absolute_import, division, unicode_literals)

from .constants import WHITESPACE
from .utils import inc_tuple, dec_tuple, LineCol, position_between

class NodeWithPosition(object):

    def __init__(self, last, first):
        self.first_line, self.first_col = first
        self.uid = self.last_line, self.last_col = last


def nprint(node):
    print(dir(node))
    print(node.lineno, node.col_offset)


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