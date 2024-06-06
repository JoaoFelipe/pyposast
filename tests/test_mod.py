# Copyright (c) 2015 Universidade Federal Fluminense (UFF)
# This file is part of PyPosAST.
# Please, consult the license terms in the LICENSE file.

from __future__ import (absolute_import, division)

import ast

from .utils import NodeTestCase
from pyposast import get_nodes
from pyposast.cross_version import ge_python38


class TestMod(NodeTestCase):

    def test_module(self):
        code = ("#bla\n"
                "")
        nodes = get_nodes(code, ast.Module)
        self.assertPosition(nodes[0], (0, 0), (0, 0), (0, 0))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_module2(self):
        code = ("#bla\n"
                "a")
        nodes = get_nodes(code, ast.Module)
        self.assertPosition(nodes[0], (2, 0), (2, 1), (2, 1))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_interactive(self):
        code = ("a")
        nodes = get_nodes(code, ast.Interactive, mode='single')
        self.assertPosition(nodes[0], (1, 0), (1, 1), (1, 1))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_expression(self):
        code = ("a")
        nodes = get_nodes(code, ast.Expression, mode='eval')
        self.assertPosition(nodes[0], (1, 0), (1, 1), (1, 1))
        self.assertNoBeforeInnerAfter(nodes[0])

    @ge_python38
    def test_type_ignore(self):
        code = ("# type: ignore\n"
                "def f():\n"
                "    # type: ignore x\n"
                "    pass")
        nodes = get_nodes(code, ast.TypeIgnore, type_comments=True)
        self.assertPosition(nodes[0], (1, 2), (1, 14), (1, 14))
        self.assertPosition(nodes[1], (3, 6), (3, 20), (3, 20))