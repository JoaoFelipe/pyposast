# Copyright (c) 2016 Universidade Federal Fluminense (UFF)
# This file is part of PyPosAST.
# Please, consult the license terms in the LICENSE file.
"""PyPosAST Module"""
from __future__ import (absolute_import, division)

import ast
from .visitor import LineProvenanceVisitor as Visitor, extract_code
from .cross_version import native_decode_source, decode_source_to_unicode


def parse(code, filename='<unknown>', mode='exec', tree=None):
    """Parse the source into an AST node with PyPosAST.
    Enhance nodes with positions


    Arguments:
    code -- code text


    Keyword Arguments:
    filename -- code path
    mode -- execution mode (exec, eval, single)
    tree -- current tree, if it was optimized
    """
    visitor = Visitor(code, filename, mode, tree=tree)
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


def get_nodes(code, desired_type, path="__main__", mode="exec", tree=None):
    """Find all nodes of a given type


    Arguments:
    code -- code text
    desired_type -- ast Node or tuple


    Keyword Arguments:
    path -- code path
    mode -- execution mode (exec, eval, single)
    tree -- current tree, if it was optimized
    """
    return _GetVisitor(parse(code, path, mode, tree), desired_type).result

