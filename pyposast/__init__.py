# Copyright (c) 2016 Universidade Federal Fluminense (UFF)
# This file is part of PyPosAST.
# Please, consult the license terms in the LICENSE file.
"""PyPosAST Module"""
from __future__ import (absolute_import, division)

import ast
from .visitor import LineProvenanceVisitor as Visitor


def parse(code, filename='<unknown>', mode='exec'):
    """Parse the source into an AST node with PyPosAST.
    Enhance nodes with positions


    Arguments:
    code -- code text


    Keyword Arguments:
    filename -- code path
    mode -- execution mode (exec, eval, single)
    """
    visitor = Visitor(code, filename, mode)
    return visitor.tree


class _GetVisitor(ast.NodeVisitor):
    """Visit nodes and store them in .result if they match the given type"""

    def __init__(self, tree, desired_type):
        self.desired_type = desired_type
        self.result = []
        self.visit(tree)

    def generic_visit(self, node):
        if isinstance(node, self.desired_type):
            self.result.append(node)
        return ast.NodeVisitor.generic_visit(self, node)


def get_nodes(code, desired_type, path="__main__", mode="exec"):
    """Find all nodes of a given type


    Arguments:
    code -- code text
    desired_type -- ast Node or tuple
    """
    return _GetVisitor(parse(code, path, mode), desired_type).result


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
