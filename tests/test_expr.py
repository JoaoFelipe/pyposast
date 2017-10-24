# coding: utf-8
# Copyright (c) 2016 Universidade Federal Fluminense (UFF)
# This file is part of PyPosAST.
# Please, consult the license terms in the LICENSE file.

from __future__ import (absolute_import, division)

import ast

from .utils import get_nodes, NodeTestCase
from .utils import only_python2, only_python3, only_python35, only_python36


def nprint(nodes):
    """Print nodes"""
    for i, node in enumerate(nodes):
        print(i, node.lineno, node.col_offset)


class TestExpr(NodeTestCase):
    # pylint: disable=missing-docstring, too-many-public-methods

    def test_name(self):
        code = ("#bla\n"
                "abc")
        nodes = get_nodes(code, ast.Name)
        self.assertPosition(nodes[0], (2, 0), (2, 3), (2, 3))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_name2(self):
        code = ("#bla\n"
                "(z)")
        nodes = get_nodes(code, ast.Name)
        self.assertPosition(nodes[0], (2, 0), (2, 3), (2, 3))
        self.assertSimpleInnerPosition(nodes[0], (2, 1), (2, 2))

    def test_name3(self):
        code = ("#bla\n"
                "( z )")
        nodes = get_nodes(code, ast.Name)
        self.assertPosition(nodes[0], (2, 0), (2, 5), (2, 5))
        self.assertSimpleInnerPosition(nodes[0], (2, 2), (2, 3))

    def test_name4(self):
        code = ("#bla\n"
                "((z))")
        nodes = get_nodes(code, ast.Name)
        self.assertPosition(nodes[0], (2, 0), (2, 5), (2, 5))
        self.assertSimpleInnerPosition(nodes[0], (2, 2), (2, 3))

    def test_name5(self):
        code = ("#bla\n"
                "((z\n"
                "))")
        nodes = get_nodes(code, ast.Name)
        self.assertPosition(nodes[0], (2, 0), (3, 2), (3, 2))
        self.assertSimpleInnerPosition(nodes[0], (2, 2), (3, 0))

    def test_num(self):
        code = ("#bla\n"
                "12")
        nodes = get_nodes(code, ast.Num)
        self.assertPosition(nodes[0], (2, 0), (2, 2), (2, 2))
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python2
    def test_num2(self):
        """ Python 3 Num uses the minus as unaryop, USub """
        code = ("#bla\n"
                "-  1245")
        nodes = get_nodes(code, ast.Num)
        self.assertPosition(nodes[0], (2, 0), (2, 7), (2, 7))
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python2
    def test_num3(self):
        """ Python 3 Num uses the minus as unaryop, USub """
        code = ("#bla\n"
                "-  0")
        nodes = get_nodes(code, ast.Num)
        self.assertPosition(nodes[0], (2, 0), (2, 4), (2, 4))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_num4(self):
        code = ("#bla\n"
                "0x1245")
        nodes = get_nodes(code, ast.Num)
        self.assertPosition(nodes[0], (2, 0), (2, 6), (2, 6))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_num5(self):
        code = ("#bla\n"
                "(2)")
        nodes = get_nodes(code, ast.Num)
        self.assertPosition(nodes[0], (2, 0), (2, 3), (2, 3))
        self.assertSimpleInnerPosition(nodes[0], (2, 1), (2, 2))

    def test_num6(self):
        code = ("#bla\n"
                "f(2)")
        nodes = get_nodes(code, ast.Num)
        self.assertPosition(nodes[0], (2, 2), (2, 3), (2, 3))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_str(self):
        code = ("#bla\n"
                "'ab\\\n"
                " cd\\\n"
                " ef'")
        nodes = get_nodes(code, ast.Str)
        self.assertPosition(nodes[0], (2, 0), (4, 4), (4, 4))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_str2(self):
        code = ("#bla\n"
                "'abcd'")
        nodes = get_nodes(code, ast.Str)
        self.assertPosition(nodes[0], (2, 0), (2, 6), (2, 6))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_str3(self):
        code = ("#bla\n"
                "('ab'\\\n"
                " 'cd'\n"
                " 'ef')")
        nodes = get_nodes(code, ast.Str)
        self.assertPosition(nodes[0], (2, 0), (4, 6), (4, 6))
        self.assertSimpleInnerPosition(nodes[0], (2, 1), (4, 5))

    def test_str4(self):
        code = ("#bla\n"
                "'ab' 'cd' 'ef'")
        nodes = get_nodes(code, ast.Str)
        self.assertPosition(nodes[0], (2, 0), (2, 14), (2, 14))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_attribute(self):
        code = ("#bla\n"
                "a.b")
        nodes = get_nodes(code, ast.Attribute)
        self.assertPosition(nodes[0], (2, 0), (2, 3), (2, 2))
        self.assertPosition(nodes[0].op_pos[0], (2, 1), (2, 2), (2, 2))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_attribute2(self):
        code = ("#bla\n"
                "a.\\\n"
                "b")
        nodes = get_nodes(code, ast.Attribute)
        self.assertPosition(nodes[0], (2, 0), (3, 1), (2, 2))
        self.assertPosition(nodes[0].op_pos[0], (2, 1), (2, 2), (2, 2))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_attribute3(self):
        code = ("#bla\n"
                "a.b.c")
        nodes = get_nodes(code, ast.Attribute)
        self.assertPosition(nodes[0], (2, 0), (2, 5), (2, 4))
        self.assertPosition(nodes[0].op_pos[0], (2, 3), (2, 4), (2, 4))
        self.assertPosition(nodes[1], (2, 0), (2, 3), (2, 2))
        self.assertPosition(nodes[1].op_pos[0], (2, 1), (2, 2), (2, 2))
        self.assertNoBeforeInnerAfter(nodes[0])
        self.assertNoBeforeInnerAfter(nodes[1])

    def test_attribute4(self):
        code = ("#bla\n"
                "a.\\\n"
                "b.c\\\n"
                ".d")
        nodes = get_nodes(code, ast.Attribute)
        self.assertPosition(nodes[0], (2, 0), (4, 2), (4, 1))
        self.assertPosition(nodes[0].op_pos[0], (4, 0), (4, 1), (4, 1))
        self.assertPosition(nodes[1], (2, 0), (3, 3), (3, 2))
        self.assertPosition(nodes[1].op_pos[0], (3, 1), (3, 2), (3, 2))
        self.assertPosition(nodes[2], (2, 0), (3, 1), (2, 2))
        self.assertPosition(nodes[2].op_pos[0], (2, 1), (2, 2), (2, 2))
        self.assertNoBeforeInnerAfter(nodes[0])
        self.assertNoBeforeInnerAfter(nodes[1])
        self.assertNoBeforeInnerAfter(nodes[2])

    def test_attribute5(self):
        code = ("#bla\n"
                "(a.\\\n"
                "   b)")
        nodes = get_nodes(code, ast.Attribute)
        self.assertPosition(nodes[0], (2, 0), (3, 5), (2, 3))
        self.assertPosition(nodes[0].op_pos[0], (2, 2), (2, 3), (2, 3))
        self.assertSimpleInnerPosition(nodes[0], (2, 1), (3, 4))

    def test_ellipsis(self):
        code = ("#bla\n"
                "a[...]")
        nodes = get_nodes(code, ast.Ellipsis)
        self.assertPosition(nodes[0], (2, 2), (2, 5), (2, 5))
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python2
    def test_ellipsis2(self):
        """ Invalid Python 3 syntax """
        code = ("#bla\n"
                "a[.\\\n"
                "..]")
        nodes = get_nodes(code, ast.Ellipsis)
        self.assertPosition(nodes[0], (2, 2), (3, 2), (3, 2))
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python3
    def test_ellipsis3(self):
        """ Invalid Python 2 syntax """
        code = ("#bla\n"
                "a[(...)]")
        nodes = get_nodes(code, ast.Ellipsis)
        self.assertPosition(nodes[0], (2, 2), (2, 7), (2, 7))
        self.assertSimpleInnerPosition(nodes[0], (2, 3), (2, 6))

    def test_subscript(self):
        code = ("#bla\n"
                "a\\\n"
                "[1]")
        nodes = get_nodes(code, ast.Subscript)
        self.assertPosition(nodes[0], (2, 0), (3, 3), (3, 3))
        self.assertPosition(nodes[0].op_pos[0], (3, 0), (3, 1), (3, 1))
        self.assertPosition(nodes[0].op_pos[1], (3, 2), (3, 3), (3, 3))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_subscript2(self):
        code = ("#bla\n"
                "a[\n"
                "1]")
        nodes = get_nodes(code, ast.Subscript)
        self.assertPosition(nodes[0], (2, 0), (3, 2), (3, 2))
        self.assertPosition(nodes[0].op_pos[0], (2, 1), (2, 2), (2, 2))
        self.assertPosition(nodes[0].op_pos[1], (3, 1), (3, 2), (3, 2))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_subscript3(self):
        code = ("#bla\n"
                "a[1:\n"
                "2,\n"
                "3 ]")
        nodes = get_nodes(code, ast.Subscript)
        self.assertPosition(nodes[0], (2, 0), (4, 3), (4, 3))
        self.assertPosition(nodes[0].op_pos[0], (2, 1), (2, 2), (2, 2))
        self.assertPosition(nodes[0].op_pos[1], (4, 2), (4, 3), (4, 3))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_subscript4(self):
        code = ("#bla\n"
                "(a\n"
                "[1])")
        nodes = get_nodes(code, ast.Subscript)
        self.assertPosition(nodes[0], (2, 0), (3, 4), (3, 4))
        self.assertPosition(nodes[0].op_pos[0], (3, 0), (3, 1), (3, 1))
        self.assertPosition(nodes[0].op_pos[1], (3, 2), (3, 3), (3, 3))
        self.assertSimpleInnerPosition(nodes[0], (2, 1), (3, 3))

    def test_subscript5(self):
        code = (u"#bla\n"
                u"f('Ç', ns['u'])\n")
        nodes = get_nodes(code, ast.Subscript)
        self.assertPosition(nodes[0], (2, 7), (2, 14), (2, 14))
        self.assertPosition(nodes[0].op_pos[0], (2, 9), (2, 10), (2, 10))
        self.assertPosition(nodes[0].op_pos[1], (2, 13), (2, 14), (2, 14))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_tuple(self):
        code = ("#bla\n"
                "(\n"
                "1, 2,\n"
                "3\n"
                ")")
        nodes = get_nodes(code, ast.Tuple)
        self.assertPosition(nodes[0], (2, 0), (5, 1), (3, 1))
        self.assertPosition(nodes[0].op_pos[0], (3, 1), (3, 2), (3, 2))
        self.assertPosition(nodes[0].op_pos[1], (3, 4), (3, 5), (3, 5))
        self.assertSimpleInnerPosition(nodes[0], (3, 0), (5, 0))

    def test_tuple2(self):
        code = ("#bla\n"
                "(\n"
                ")")

        nodes = get_nodes(code, ast.Tuple)
        self.assertPosition(nodes[0], (2, 0), (3, 1), (3, 1))
        self.assertNoBeforeInnerAfter(nodes[0])
        self.assertEqual(nodes[0].op_pos, [])

    def test_tuple3(self):
        code = ("#bla\n"
                "(((0),\n"
                "1, 2,\n"
                "3\n"
                "))")
        nodes = get_nodes(code, ast.Tuple)
        self.assertPosition(nodes[0], (2, 0), (5, 2), (2, 5))
        self.assertPosition(nodes[0].op_pos[0], (2, 5), (2, 6), (2, 6))
        self.assertPosition(nodes[0].op_pos[1], (3, 1), (3, 2), (3, 2))
        self.assertPosition(nodes[0].op_pos[2], (3, 4), (3, 5), (3, 5))
        self.assertSimpleInnerPosition(nodes[0], (2, 2), (5, 0))

    def test_tuple4(self):
        code = ("#bla\n"
                "1,")
        nodes = get_nodes(code, ast.Tuple)
        self.assertPosition(nodes[0], (2, 0), (2, 2), (2, 1))
        self.assertPosition(nodes[0].op_pos[0], (2, 1), (2, 2), (2, 2))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_tuple5(self):
        code = ("#bla\n"
                "([1, 2], 3)")
        nodes = get_nodes(code, ast.Tuple)
        self.assertPosition(nodes[0], (2, 0), (2, 11), (2, 7))
        self.assertPosition(nodes[0].op_pos[0], (2, 7), (2, 8), (2, 8))
        self.assertSimpleInnerPosition(nodes[0], (2, 1), (2, 10))

    def test_tuple6(self):
        code = ("#bla\n"
                "1, 2  ,")
        nodes = get_nodes(code, ast.Tuple)
        self.assertPosition(nodes[0], (2, 0), (2, 7), (2, 1))
        self.assertPosition(nodes[0].op_pos[0], (2, 1), (2, 2), (2, 2))
        self.assertPosition(nodes[0].op_pos[1], (2, 6), (2, 7), (2, 7))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_list(self):
        code = ("#bla\n"
                "[\n"
                "1, 2,\n"
                "3\n"
                "]")
        nodes = get_nodes(code, ast.List)
        self.assertPosition(nodes[0], (2, 0), (5, 1), (5, 1))
        self.assertPosition(nodes[0].op_pos[0], (3, 1), (3, 2), (3, 2))
        self.assertPosition(nodes[0].op_pos[1], (3, 4), (3, 5), (3, 5))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_list2(self):
        code = ("#bla\n"
                "[\n"
                "]")

        nodes = get_nodes(code, ast.List)
        self.assertPosition(nodes[0], (2, 0), (3, 1), (3, 1))
        self.assertEqual(nodes[0].op_pos, [])
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_list3(self):
        code = ("#bla\n"
                "([(0),\n"
                "1, 2,\n"
                "3\n"
                "])")
        nodes = get_nodes(code, ast.List)
        self.assertPosition(nodes[0], (2, 0), (5, 2), (5, 2))
        self.assertPosition(nodes[0].op_pos[0], (2, 5), (2, 6), (2, 6))
        self.assertPosition(nodes[0].op_pos[1], (3, 1), (3, 2), (3, 2))
        self.assertPosition(nodes[0].op_pos[2], (3, 4), (3, 5), (3, 5))
        self.assertSimpleInnerPosition(nodes[0], (2, 1), (5, 1))

    @only_python2
    def test_repr(self):
        code = ("#bla\n"
                "`1`")
        nodes = get_nodes(code, ast.Repr)
        self.assertPosition(nodes[0], (2, 0), (2, 3), (2, 3))
        self.assertPosition(nodes[0].op_pos[0], (2, 0), (2, 1), (2, 1))
        self.assertPosition(nodes[0].op_pos[1], (2, 2), (2, 3), (2, 3))
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python2
    def test_repr2(self):
        code = ("#bla\n"
                "``1``")
        nodes = get_nodes(code, ast.Repr)
        self.assertPosition(nodes[0], (2, 0), (2, 5), (2, 5))
        self.assertPosition(nodes[0].op_pos[0], (2, 0), (2, 1), (2, 1))
        self.assertPosition(nodes[0].op_pos[1], (2, 4), (2, 5), (2, 5))
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python2
    def test_repr3(self):
        code = ("#bla\n"
                "``2\\\n"
                "``")
        nodes = get_nodes(code, ast.Repr)
        self.assertPosition(nodes[0], (2, 0), (3, 2), (3, 2))
        self.assertPosition(nodes[0].op_pos[0], (2, 0), (2, 1), (2, 1))
        self.assertPosition(nodes[0].op_pos[1], (3, 1), (3, 2), (3, 2))
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python2
    def test_repr4(self):
        code = ("#bla\n"
                "(``2\n"
                "``)")
        nodes = get_nodes(code, ast.Repr)
        self.assertPosition(nodes[0], (2, 0), (3, 3), (3, 3))
        self.assertPosition(nodes[0].op_pos[0], (2, 1), (2, 2), (2, 2))
        self.assertPosition(nodes[0].op_pos[1], (3, 1), (3, 2), (3, 2))
        self.assertSimpleInnerPosition(nodes[0], (2, 1), (3, 2))

    def test_call(self):
        code = ("#bla\n"
                "fn(\n"
                "2)")
        nodes = get_nodes(code, ast.Call)
        self.assertPosition(nodes[0], (2, 0), (3, 2), (3, 2))
        self.assertPosition(nodes[0].op_pos[0], (2, 2), (2, 3), (2, 3))
        self.assertPosition(nodes[0].op_pos[1], (3, 1), (3, 2), (3, 2))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_call2(self):
        code = ("#bla\n"
                "fn(\n"
                "2,)")
        nodes = get_nodes(code, ast.Call)
        self.assertPosition(nodes[0], (2, 0), (3, 3), (3, 3))
        self.assertPosition(nodes[0].op_pos[0], (2, 2), (2, 3), (2, 3))
        self.assertPosition(nodes[0].op_pos[1], (3, 1), (3, 2), (3, 2))
        self.assertPosition(nodes[0].op_pos[2], (3, 2), (3, 3), (3, 3))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_call3(self):
        code = ("#bla\n"
                "fn\\\n"
                "((\n"
                "2, 3))")
        nodes = get_nodes(code, ast.Call)
        self.assertPosition(nodes[0], (2, 0), (4, 6), (4, 6))
        self.assertPosition(nodes[0].op_pos[0], (3, 0), (3, 1), (3, 1))
        self.assertPosition(nodes[0].op_pos[1], (4, 5), (4, 6), (4, 6))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_call4(self):
        code = ("#bla\n"
                "fn()\\\n"
                "((\n"
                "2, 3))")
        nodes = get_nodes(code, ast.Call)
        self.assertPosition(nodes[0], (2, 0), (4, 6), (4, 6))
        self.assertPosition(nodes[1], (2, 0), (2, 4), (2, 4))
        self.assertPosition(nodes[0].op_pos[0], (3, 0), (3, 1), (3, 1))
        self.assertPosition(nodes[0].op_pos[1], (4, 5), (4, 6), (4, 6))
        self.assertNoBeforeInnerAfter(nodes[0])
        self.assertPosition(nodes[1].op_pos[0], (2, 2), (2, 3), (2, 3))
        self.assertPosition(nodes[1].op_pos[1], (2, 3), (2, 4), (2, 4))
        self.assertNoBeforeInnerAfter(nodes[1])

    def test_call5(self):
        code = ("#bla\n"
                "(fn(\n"
                "2))")
        nodes = get_nodes(code, ast.Call)
        self.assertPosition(nodes[0], (2, 0), (3, 3), (3, 3))
        self.assertPosition(nodes[0].op_pos[0], (2, 3), (2, 4), (2, 4))
        self.assertPosition(nodes[0].op_pos[1], (3, 1), (3, 2), (3, 2))
        self.assertSimpleInnerPosition(nodes[0], (2, 1), (3, 2))

    def test_compare(self):
        code = ("#bla\n"
                "2 < 3")
        nodes = get_nodes(code, ast.Compare)
        self.assertPosition(nodes[0], (2, 0), (2, 5), (2, 5))
        self.assertPosition(nodes[0].op_pos[0], (2, 2), (2, 3), (2, 3))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_compare2(self):
        code = ("#bla\n"
                "2 < 3 <\\\n"
                " 5")
        nodes = get_nodes(code, ast.Compare)
        self.assertPosition(nodes[0], (2, 0), (3, 2), (3, 2))
        self.assertPosition(nodes[0].op_pos[0], (2, 2), (2, 3), (2, 3))
        self.assertPosition(nodes[0].op_pos[1], (2, 6), (2, 7), (2, 7))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_compare3(self):
        code = ("#bla\n"
                "(2 < 3 <\n"
                " 5)")
        nodes = get_nodes(code, ast.Compare)
        self.assertPosition(nodes[0], (2, 0), (3, 3), (3, 3))
        self.assertPosition(nodes[0].op_pos[0], (2, 3), (2, 4), (2, 4))
        self.assertPosition(nodes[0].op_pos[1], (2, 7), (2, 8), (2, 8))
        self.assertSimpleInnerPosition(nodes[0], (2, 1), (3, 2))

    @only_python35
    def test_await(self):
        code = ("async def f():\n"
                "    await   2")
        nodes = get_nodes(code, ast.Await)
        self.assertPosition(nodes[0], (2, 4), (2, 13), (2, 9))
        self.assertPosition(nodes[0].op_pos[0], (2, 4), (2, 9), (2, 9))
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python35
    def test_await2(self):
        code = ("async def f():\n"
                "    (await \n"
                "2)")
        nodes = get_nodes(code, ast.Await)
        self.assertPosition(nodes[0], (2, 4), (3, 2), (2, 10))
        self.assertPosition(nodes[0].op_pos[0], (2, 5), (2, 10), (2, 10))
        self.assertSimpleInnerPosition(nodes[0], (2, 5), (3, 1))

    def test_yield(self):
        code = ("#bla\n"
                "yield   2")
        nodes = get_nodes(code, ast.Yield)
        self.assertPosition(nodes[0], (2, 0), (2, 9), (2, 5))
        self.assertPosition(nodes[0].op_pos[0], (2, 0), (2, 5), (2, 5))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_yield2(self):
        code = ("#bla\n"
                "(yield \n"
                "2)")
        nodes = get_nodes(code, ast.Yield)
        self.assertPosition(nodes[0], (2, 0), (3, 2), (2, 6))
        self.assertPosition(nodes[0].op_pos[0], (2, 1), (2, 6), (2, 6))
        self.assertSimpleInnerPosition(nodes[0], (2, 1), (3, 1))

    def test_yield3(self):
        code = ("#bla\n"
                "yield")
        nodes = get_nodes(code, ast.Yield)
        self.assertPosition(nodes[0], (2, 0), (2, 5), (2, 5))
        self.assertPosition(nodes[0].op_pos[0], (2, 0), (2, 5), (2, 5))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_generator_exp(self):
        code = ("#bla\n"
                "f(x\n"
                " for x in l\n"
                " if x)")
        nodes = get_nodes(code, ast.GeneratorExp)
        self.assertPosition(nodes[0], (2, 2), (4, 5), (2, 3))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_dict_comp(self):
        code = ("#bla\n"
                "{x:2\n"
                " for x in l\n"
                " if x}")
        nodes = get_nodes(code, ast.DictComp)
        self.assertPosition(nodes[0], (2, 0), (4, 6), (4, 6))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_dict_comp2(self):
        code = ("#bla\n"
                "({x:2\n"
                " for x in l\n"
                " if x})")
        nodes = get_nodes(code, ast.DictComp)
        self.assertPosition(nodes[0], (2, 0), (4, 7), (4, 7))
        self.assertSimpleInnerPosition(nodes[0], (2, 1), (4, 6))

    def test_set_comp(self):
        code = ("#bla\n"
                "{x\n"
                " for x in l\n"
                " if x}")
        nodes = get_nodes(code, ast.SetComp)
        self.assertPosition(nodes[0], (2, 0), (4, 6), (4, 6))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_set_comp2(self):
        code = ("#bla\n"
                "({x\n"
                " for x in l\n"
                " if x})")
        nodes = get_nodes(code, ast.SetComp)
        self.assertPosition(nodes[0], (2, 0), (4, 7), (4, 7))
        self.assertSimpleInnerPosition(nodes[0], (2, 1), (4, 6))

    def test_list_comp(self):
        code = ("#bla\n"
                "[x\n"
                " for x in l\n"
                " if x]")
        nodes = get_nodes(code, ast.ListComp)
        self.assertPosition(nodes[0], (2, 0), (4, 6), (4, 6))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_list_comp2(self):
        code = ("#bla\n"
                "([x\n"
                " for x in l\n"
                " if x])")
        nodes = get_nodes(code, ast.ListComp)
        self.assertPosition(nodes[0], (2, 0), (4, 7), (4, 7))
        self.assertSimpleInnerPosition(nodes[0], (2, 1), (4, 6))

    @only_python36
    def test_async_comp(self):
        code = ("#bla\n"
                "async def f():\n"
                "    [x\n"
                "     async for x in l\n"
                "     if x]")
        nodes = get_nodes(code, ast.ListComp)
        self.assertPosition(nodes[0], (3, 4), (5, 10), (5, 10))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_set(self):
        code = ("#bla\n"
                "{x,\n"
                " 1,\n"
                " 3}")
        nodes = get_nodes(code, ast.Set)
        self.assertPosition(nodes[0], (2, 0), (4, 3), (4, 3))
        self.assertPosition(nodes[0].op_pos[0], (2, 2), (2, 3), (2, 3))
        self.assertPosition(nodes[0].op_pos[1], (3, 2), (3, 3), (3, 3))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_set2(self):
        code = ("#bla\n"
                "({x,\n"
                " 1,\n"
                " 3})")
        nodes = get_nodes(code, ast.Set)
        self.assertPosition(nodes[0], (2, 0), (4, 4), (4, 4))
        self.assertPosition(nodes[0].op_pos[0], (2, 3), (2, 4), (2, 4))
        self.assertPosition(nodes[0].op_pos[1], (3, 2), (3, 3), (3, 3))
        self.assertSimpleInnerPosition(nodes[0], (2, 1), (4, 3))

    def test_dict(self):
        code = ("#bla\n"
                "{}")
        nodes = get_nodes(code, ast.Dict)
        self.assertPosition(nodes[0], (2, 0), (2, 2), (2, 2))
        self.assertEqual(nodes[0].op_pos, [])
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_dict2(self):
        code = ("#bla\n"
                "{1}, {1: x,\n"
                "  2: 1,\n"
                "  3: 3}")
        nodes = get_nodes(code, ast.Dict)
        self.assertPosition(nodes[0], (2, 5), (4, 7), (4, 7))
        self.assertPosition(nodes[0].op_pos[0], (2, 7), (2, 8), (2, 8))
        self.assertPosition(nodes[0].op_pos[1], (2, 10), (2, 11), (2, 11))

        self.assertPosition(nodes[0].op_pos[2], (3, 3), (3, 4), (3, 4))
        self.assertPosition(nodes[0].op_pos[3], (3, 6), (3, 7), (3, 7))

        self.assertPosition(nodes[0].op_pos[4], (4, 3), (4, 4), (4, 4))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_dict3(self):
        code = ("#bla\n"
                "{1}, ({1: x,\n"
                "  2: 1,\n"
                "  3: 3})")
        nodes = get_nodes(code, ast.Dict)
        self.assertPosition(nodes[0], (2, 5), (4, 8), (4, 8))
        self.assertPosition(nodes[0].op_pos[0], (2, 8), (2, 9), (2, 9))
        self.assertPosition(nodes[0].op_pos[1], (2, 11), (2, 12), (2, 12))

        self.assertPosition(nodes[0].op_pos[2], (3, 3), (3, 4), (3, 4))
        self.assertPosition(nodes[0].op_pos[3], (3, 6), (3, 7), (3, 7))

        self.assertPosition(nodes[0].op_pos[4], (4, 3), (4, 4), (4, 4))
        self.assertSimpleInnerPosition(nodes[0], (2, 6), (4, 7))

    def test_if_exp(self):
        code = ("#bla\n"
                "1 if 2\\\n"
                "  else 3")
        nodes = get_nodes(code, ast.IfExp)
        self.assertPosition(nodes[0], (2, 0), (3, 8), (2, 4))
        self.assertPosition(nodes[0].op_pos[0], (2, 2), (2, 4), (2, 4))
        self.assertPosition(nodes[0].op_pos[1], (3, 2), (3, 6), (3, 6))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_if_exp2(self):
        code = ("#bla\n"
                "(1 if 2\n"
                "  else 3)")
        nodes = get_nodes(code, ast.IfExp)
        self.assertPosition(nodes[0], (2, 0), (3, 9), (2, 5))
        self.assertPosition(nodes[0].op_pos[0], (2, 3), (2, 5), (2, 5))
        self.assertPosition(nodes[0].op_pos[1], (3, 2), (3, 6), (3, 6))
        self.assertSimpleInnerPosition(nodes[0], (2, 1), (3, 8))

    def test_lambda(self):
        code = ("#bla\n"
                "lambda x, y:\\\n"
                "x")
        nodes = get_nodes(code, ast.Lambda)
        self.assertPosition(nodes[0], (2, 0), (3, 1), (2, 12))
        self.assertPosition(nodes[0].op_pos[0], (2, 0), (2, 6), (2, 6))
        self.assertPosition(nodes[0].op_pos[1], (2, 11), (2, 12), (2, 12))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_lambda2(self):
        code = ("#bla\n"
                "(lambda x, y:\n"
                "x)")
        nodes = get_nodes(code, ast.Lambda)
        self.assertPosition(nodes[0], (2, 0), (3, 2), (2, 13))
        self.assertPosition(nodes[0].op_pos[0], (2, 1), (2, 7), (2, 7))
        self.assertPosition(nodes[0].op_pos[1], (2, 12), (2, 13), (2, 13))
        self.assertSimpleInnerPosition(nodes[0], (2, 1), (3, 1))

    def test_unary_op(self):
        code = ("#bla\n"
                "- a")
        nodes = get_nodes(code, ast.UnaryOp)
        self.assertPosition(nodes[0], (2, 0), (2, 3), (2, 1))
        self.assertPosition(nodes[0].op_pos[0], (2, 0), (2, 1), (2, 1))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_unary_op2(self):
        code = ("#bla\n"
                "(-\n"
                "a)")
        nodes = get_nodes(code, ast.UnaryOp)
        self.assertPosition(nodes[0], (2, 0), (3, 2), (2, 2))
        self.assertPosition(nodes[0].op_pos[0], (2, 1), (2, 2), (2, 2))
        self.assertSimpleInnerPosition(nodes[0], (2, 1), (3, 1))

    def test_binop(self):
        code = ("#bla\n"
                "ab+a")
        nodes = get_nodes(code, ast.BinOp)
        self.assertPosition(nodes[0], (2, 0), (2, 4), (2, 3))
        self.assertPosition(nodes[0].op_pos[0], (2, 2), (2, 3), (2, 3))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_binop2(self):
        code = ("#bla\n"
                "a * b + c")
        nodes = get_nodes(code, ast.BinOp)
        self.assertPosition(nodes[0], (2, 0), (2, 9), (2, 7))
        self.assertPosition(nodes[0].op_pos[0], (2, 6), (2, 7), (2, 7))
        self.assertNoBeforeInnerAfter(nodes[0])
        self.assertPosition(nodes[1], (2, 0), (2, 5), (2, 3))
        self.assertPosition(nodes[1].op_pos[0], (2, 2), (2, 3), (2, 3))
        self.assertNoBeforeInnerAfter(nodes[1])

    def test_binop3(self):
        code = ("#bla\n"
                "(b + a)")
        nodes = get_nodes(code, ast.BinOp)
        self.assertPosition(nodes[0], (2, 0), (2, 7), (2, 4))
        self.assertPosition(nodes[0].op_pos[0], (2, 3), (2, 4), (2, 4))
        self.assertSimpleInnerPosition(nodes[0], (2, 1), (2, 6))

    def test_bool_op(self):
        code = ("#bla\n"
                "a and b and c")
        nodes = get_nodes(code, ast.BoolOp)
        self.assertPosition(nodes[0], (2, 0), (2, 13), (2, 13))
        self.assertPosition(nodes[0].op_pos[0], (2, 2), (2, 5), (2, 5))
        self.assertPosition(nodes[0].op_pos[1], (2, 8), (2, 11), (2, 11))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_bool_op2(self):
        code = ("#bla\n"
                "a and b or c")
        nodes = get_nodes(code, ast.BoolOp)
        self.assertPosition(nodes[0], (2, 0), (2, 12), (2, 12))
        self.assertPosition(nodes[0].op_pos[0], (2, 8), (2, 10), (2, 10))
        self.assertNoBeforeInnerAfter(nodes[0])
        self.assertPosition(nodes[1], (2, 0), (2, 7), (2, 7))
        self.assertPosition(nodes[1].op_pos[0], (2, 2), (2, 5), (2, 5))
        self.assertNoBeforeInnerAfter(nodes[1])

    def test_bool_op3(self):
        code = ("#bla\n"
                "(a and b and c)")
        nodes = get_nodes(code, ast.BoolOp)
        self.assertPosition(nodes[0], (2, 0), (2, 15), (2, 15))
        self.assertPosition(nodes[0].op_pos[0], (2, 3), (2, 6), (2, 6))
        self.assertPosition(nodes[0].op_pos[1], (2, 9), (2, 12), (2, 12))
        self.assertSimpleInnerPosition(nodes[0], (2, 1), (2, 14))

    @only_python3
    def test_starred(self):
        code = ("#bla\n"
                "a, * b = 1, 2, 3")
        nodes = get_nodes(code, ast.Starred)
        self.assertPosition(nodes[0], (2, 3), (2, 6), (2, 4))
        self.assertPosition(nodes[0].op_pos[0], (2, 3), (2, 4), (2, 4))
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python3
    def test_starred2(self):
        code = ("#bla\n"
                "a, (* b) = 1, 2, 3")
        nodes = get_nodes(code, ast.Starred)
        self.assertPosition(nodes[0], (2, 3), (2, 8), (2, 5))
        self.assertPosition(nodes[0].op_pos[0], (2, 4), (2, 5), (2, 5))
        self.assertSimpleInnerPosition(nodes[0], (2, 4), (2, 7))

    @only_python3
    def test_starred3(self):
        code = ("#bla\n"
                "a, *b = 1, 2, 3")
        nodes = get_nodes(code, ast.Starred)
        self.assertPosition(nodes[0], (2, 3), (2, 5), (2, 4))
        self.assertPosition(nodes[0].op_pos[0], (2, 3), (2, 4), (2, 4))
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python35
    def test_starred4(self):
        code = ("#bla\n"
                "f(*a, 5, *b)")
        nodes = get_nodes(code, ast.Starred)
        self.assertPosition(nodes[0], (2, 2), (2, 4), (2, 3))
        self.assertPosition(nodes[0].op_pos[0], (2, 2), (2, 3), (2, 3))
        self.assertNoBeforeInnerAfter(nodes[0])
        self.assertPosition(nodes[1], (2, 9), (2, 11), (2, 10))
        self.assertPosition(nodes[1].op_pos[0], (2, 9), (2, 10), (2, 10))
        self.assertNoBeforeInnerAfter(nodes[1])

    @only_python35
    def test_starred5(self):
        code = ("#bla\n"
                "i, j, k, l, m = *a, 5, *b")
        nodes = get_nodes(code, ast.Starred)
        self.assertPosition(nodes[0], (2, 16), (2, 18), (2, 17))
        self.assertPosition(nodes[0].op_pos[0], (2, 16), (2, 17), (2, 17))
        self.assertNoBeforeInnerAfter(nodes[0])
        self.assertPosition(nodes[1], (2, 23), (2, 25), (2, 24))
        self.assertPosition(nodes[1].op_pos[0], (2, 23), (2, 24), (2, 24))
        self.assertNoBeforeInnerAfter(nodes[1])

    @only_python3
    def test_name_constant(self):
        code = ("#bla\n"
                "None")
        nodes = get_nodes(code, ast.NameConstant)
        self.assertPosition(nodes[0], (2, 0), (2, 4), (2, 4))
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python3
    def test_name_constant2(self):
        code = ("#bla\n"
                "True")
        nodes = get_nodes(code, ast.NameConstant)
        self.assertPosition(nodes[0], (2, 0), (2, 4), (2, 4))
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python3
    def test_name_constant3(self):
        code = ("#bla\n"
                "False")
        nodes = get_nodes(code, ast.NameConstant)
        self.assertPosition(nodes[0], (2, 0), (2, 5), (2, 5))
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python3
    def test_name_constant4(self):
        code = ("#bla\n"
                "(None)")
        nodes = get_nodes(code, ast.NameConstant)
        self.assertPosition(nodes[0], (2, 0), (2, 6), (2, 6))
        self.assertSimpleInnerPosition(nodes[0], (2, 1), (2, 5))

    @only_python3
    def test_bytes(self):
        code = ("#bla\n"
                "b'ab\\\n"
                " cd\\\n"
                " ef'")
        nodes = get_nodes(code, ast.Bytes)
        self.assertPosition(nodes[0], (2, 0), (4, 4), (4, 4))
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python3
    def test_bytes2(self):
        code = ("#bla\n"
                "b'abcd'")
        nodes = get_nodes(code, ast.Bytes)
        self.assertPosition(nodes[0], (2, 0), (2, 7), (2, 7))
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python3
    def test_bytes3(self):
        code = ("#bla\n"
                "(b'ab'\\\n"
                " b'cd'\n"
                " b'ef')")
        nodes = get_nodes(code, ast.Bytes)
        self.assertPosition(nodes[0], (2, 0), (4, 7), (4, 7))
        self.assertSimpleInnerPosition(nodes[0], (2, 1), (4, 6))

    @only_python3
    def test_bytes4(self):
        code = ("#bla\n"
                "b'ab' b'cd' b'ef'")
        nodes = get_nodes(code, ast.Bytes)
        self.assertPosition(nodes[0], (2, 0), (2, 17), (2, 17))
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python3
    def test_yield_from(self):
        code = ("#bla\n"
                "yield from  2")
        nodes = get_nodes(code, ast.YieldFrom)
        self.assertPosition(nodes[0], (2, 0), (2, 13), (2, 10))
        self.assertPosition(nodes[0].op_pos[0], (2, 0), (2, 10), (2, 10))
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python3
    def test_yield_from2(self):
        code = ("#bla\n"
                "yield  \\\n"
                " from  2")
        nodes = get_nodes(code, ast.YieldFrom)
        self.assertPosition(nodes[0], (2, 0), (3, 8), (3, 5))
        self.assertPosition(nodes[0].op_pos[0], (2, 0), (3, 5), (3, 5))
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python3
    def test_yield_from3(self):
        code = ("#bla\n"
                "(yield  \n"
                "from  2)")
        nodes = get_nodes(code, ast.YieldFrom)
        self.assertPosition(nodes[0], (2, 0), (3, 8), (3, 4))
        self.assertPosition(nodes[0].op_pos[0], (2, 1), (3, 4), (3, 4))
        self.assertSimpleInnerPosition(nodes[0], (2, 1), (3, 7))

    @only_python36
    def test_joined_str(self):
        code = ("#bla\n"
                "a = 2\n"
                "f'{a}'\n")
        nodes = get_nodes(code, ast.JoinedStr)
        self.assertPosition(nodes[0], (3, 0), (3, 6), (3, 6))
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python36
    def test_formatted_value(self):
        code = ("#bla\n"
                "a = 2\n"
                "f'{a}'\n")
        nodes = get_nodes(code, ast.FormattedValue)
        names = get_nodes(code, ast.Name)
        self.assertPosition(nodes[0], (3, 2), (3, 5), (3, 5))
        self.assertNoBeforeInnerAfter(nodes[0])
        self.assertPosition(names[0], (2, 0), (2, 1), (2, 1))
        self.assertNoBeforeInnerAfter(names[0])
        self.assertPosition(names[1], (3, 3), (3, 4), (3, 4))
        self.assertNoBeforeInnerAfter(names[1])

    @only_python36
    def test_formatted_value2(self):
        code = ("#bla\n"
                "import decimal\n"
                "width, precision = 10, 4\n"
                "value = decimal.Decimal('12.34567')\n"
                "f'result: {value:{width}.{precision}}'\n")
        nodes = get_nodes(code, ast.FormattedValue)
        self.assertPosition(nodes[0], (5, 10), (5, 37), (5, 37))
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python36
    def test_formatted_value3(self):
        code = ("#bla\n"
                "a = 1\n"
                "b = 2\n"
                "d = f'a: {a}; b: {b}'\n"
                "# other")
        nodes = get_nodes(code, ast.FormattedValue)
        self.assertPosition(nodes[0], (4, 9), (4, 12), (4, 12))
        self.assertPosition(nodes[1], (4, 17), (4, 20), (4, 20))
        self.assertNoBeforeInnerAfter(nodes[0])
        self.assertNoBeforeInnerAfter(nodes[1])

    @only_python36
    def test_constant(self):
        code = ("#bla\n"
                "x = 2\n")

        # Constants are created by optimizers
        # Thus, we must simulate an optimizer
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Num):
                node.value = ast.copy_location(
                    ast.Constant(node.value.n),
                    node.value
                )

        nodes = get_nodes(code, ast.Constant, tree=tree)
        self.assertPosition(nodes[0], (2, 4), (2, 5), (2, 5))
        self.assertNoBeforeInnerAfter(nodes[0])
