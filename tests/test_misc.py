# Copyright (c) 2016 Universidade Federal Fluminense (UFF)
# This file is part of PyPosAST.
# Please, consult the license terms in the LICENSE file.

from __future__ import (absolute_import, division)

import ast

from .utils import get_nodes, NodeTestCase
from .utils import only_python2, only_python3, only_python35, only_python36


class TestMisc(NodeTestCase):
    # pylint: disable=missing-docstring, too-many-public-methods

    def test_index(self):
        code = ("#bla\n"
                "a[1]")
        nodes = get_nodes(code, ast.Index)
        self.assertPosition(nodes[0], (2, 2), (2, 3), (2, 3))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_slice(self):
        code = ("#bla\n"
                "a[1:2:3]")
        nodes = get_nodes(code, ast.Slice)
        self.assertPosition(nodes[0], (2, 2), (2, 7), (2, 4))
        self.assertPosition(nodes[0].op_pos[0], (2, 3), (2, 4), (2, 4))
        self.assertPosition(nodes[0].op_pos[1], (2, 5), (2, 6), (2, 6))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_slice2(self):
        code = ("#bla\n"
                "a[:\\\n"
                "2:3]")
        nodes = get_nodes(code, ast.Slice)
        self.assertPosition(nodes[0], (2, 2), (3, 3), (2, 3))
        self.assertPosition(nodes[0].op_pos[0], (2, 2), (2, 3), (2, 3))
        self.assertPosition(nodes[0].op_pos[1], (3, 1), (3, 2), (3, 2))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_slice3(self):
        code = ("#bla\n"
                "a[:\\\n"
                ":2]")
        nodes = get_nodes(code, ast.Slice)
        self.assertPosition(nodes[0], (2, 2), (3, 2), (2, 3))
        self.assertPosition(nodes[0].op_pos[0], (2, 2), (2, 3), (2, 3))
        self.assertPosition(nodes[0].op_pos[1], (3, 0), (3, 1), (3, 1))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_slice4(self):
        code = ("#bla\n"
                "a[:]")
        nodes = get_nodes(code, ast.Slice)
        self.assertPosition(nodes[0], (2, 2), (2, 3), (2, 3))
        self.assertPosition(nodes[0].op_pos[0], (2, 2), (2, 3), (2, 3))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_slice5(self):
        code = ("#bla\n"
                "a[::]")
        nodes = get_nodes(code, ast.Slice)
        self.assertPosition(nodes[0], (2, 2), (2, 4), (2, 3))
        self.assertPosition(nodes[0].op_pos[0], (2, 2), (2, 3), (2, 3))
        self.assertPosition(nodes[0].op_pos[1], (2, 3), (2, 4), (2, 4))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_slice6(self):
        code = ("#bla\n"
                "a[11:2\\\n"
                ":]")
        nodes = get_nodes(code, ast.Slice)
        self.assertPosition(nodes[0], (2, 2), (3, 1), (2, 5))
        self.assertPosition(nodes[0].op_pos[0], (2, 4), (2, 5), (2, 5))
        self.assertPosition(nodes[0].op_pos[1], (3, 0), (3, 1), (3, 1))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_slice7(self):
        code = ("#bla\n"
                "a[::None]")
        nodes = get_nodes(code, ast.Slice)
        self.assertPosition(nodes[0], (2, 2), (2, 8), (2, 3))
        self.assertPosition(nodes[0].op_pos[0], (2, 2), (2, 3), (2, 3))
        self.assertPosition(nodes[0].op_pos[1], (2, 3), (2, 4), (2, 4))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_slice8(self):
        code = ("s = None\n"
                "a[::]")
        nodes = get_nodes(code, ast.Slice)
        self.assertPosition(nodes[0], (2, 2), (2, 4), (2, 3))
        self.assertPosition(nodes[0].op_pos[0], (2, 2), (2, 3), (2, 3))
        self.assertPosition(nodes[0].op_pos[1], (2, 3), (2, 4), (2, 4))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_ext_slice(self):
        code = ("#bla\n"
                "a[1:2,3]")
        nodes = get_nodes(code, ast.ExtSlice)
        self.assertPosition(nodes[0], (2, 2), (2, 7), (2, 6))
        self.assertPosition(nodes[0].op_pos[0], (2, 5), (2, 6), (2, 6))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_ext_slice2(self):
        code = ("#bla\n"
                "a[1:2:,3]")
        nodes = get_nodes(code, ast.ExtSlice)
        self.assertPosition(nodes[0], (2, 2), (2, 8), (2, 7))
        self.assertPosition(nodes[0].op_pos[0], (2, 6), (2, 7), (2, 7))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_ext_slice3(self):
        code = ("#bla\n"
                "a[3,1:2:]")
        nodes = get_nodes(code, ast.ExtSlice)
        self.assertPosition(nodes[0], (2, 2), (2, 8), (2, 4))
        self.assertPosition(nodes[0].op_pos[0], (2, 3), (2, 4), (2, 4))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_eq(self):
        code = ("#bla\n"
                "2 == 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertPosition(comp, (2, 2), (2, 4), (2, 4))
        self.assertNoBeforeInnerAfter(comp)

    def test_not_eq(self):
        code = ("#bla\n"
                "2 != 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertPosition(comp, (2, 2), (2, 4), (2, 4))
        self.assertNoBeforeInnerAfter(comp)

    def test_not_eq2(self):
        """ Python 2 syntax """
        code = ("#bla\n"
                "2 != 4\n"
                "5 != 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertPosition(comp, (2, 2), (2, 4), (2, 4))
        self.assertNoBeforeInnerAfter(comp)
        comp2 = nodes[1].op_pos[0]
        self.assertPosition(comp2, (3, 2), (3, 4), (3, 4))
        self.assertNoBeforeInnerAfter(comp2)

    @only_python2
    def test_not_eq3(self):
        """ Python 2 syntax """
        code = ("#bla\n"
                "2 <> 4\n"
                "5 != 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertPosition(comp, (2, 2), (2, 4), (2, 4))
        self.assertNoBeforeInnerAfter(comp)
        comp2 = nodes[1].op_pos[0]
        self.assertPosition(comp2, (3, 2), (3, 4), (3, 4))
        self.assertNoBeforeInnerAfter(comp2)

    def test_lt(self):
        code = ("#bla\n"
                "2 < 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertPosition(comp, (2, 2), (2, 3), (2, 3))
        self.assertNoBeforeInnerAfter(comp)

    def test_lte(self):
        code = ("#bla\n"
                "2 <= 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertPosition(comp, (2, 2), (2, 4), (2, 4))
        self.assertNoBeforeInnerAfter(comp)

    def test_gt(self):
        code = ("#bla\n"
                "2 > 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertPosition(comp, (2, 2), (2, 3), (2, 3))
        self.assertNoBeforeInnerAfter(comp)

    def test_gte(self):
        code = ("#bla\n"
                "2 >= 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertPosition(comp, (2, 2), (2, 4), (2, 4))
        self.assertNoBeforeInnerAfter(comp)

    def test_is(self):
        code = ("#bla\n"
                "2 is 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertPosition(comp, (2, 2), (2, 4), (2, 4))
        self.assertNoBeforeInnerAfter(comp)

    def test_is2(self):
        code = ("#bla\n"
                "(2)is(4)\n"
                "(3)is(5)")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertPosition(comp, (2, 3), (2, 5), (2, 5))
        self.assertNoBeforeInnerAfter(comp)
        comp2 = nodes[1].op_pos[0]
        self.assertPosition(comp2, (3, 3), (3, 5), (3, 5))
        self.assertNoBeforeInnerAfter(comp2)

    def test_is_not(self):
        code = ("#bla\n"
                "2 is not 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertPosition(comp, (2, 2), (2, 8), (2, 8))
        self.assertNoBeforeInnerAfter(comp)

    def test_in(self):
        code = ("#bla\n"
                "2 in 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertPosition(comp, (2, 2), (2, 4), (2, 4))
        self.assertNoBeforeInnerAfter(comp)

    def test_not_in(self):
        code = ("#bla\n"
                "2 not in 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertPosition(comp, (2, 2), (2, 8), (2, 8))
        self.assertNoBeforeInnerAfter(comp)

    def test_comprehension(self):
        code = ("#bla\n"
                "[x\n"
                " for x in l\n"
                " if x]")
        nodes = get_nodes(code, ast.comprehension)
        self.assertPosition(nodes[0], (3, 1), (4, 5), (3, 4))
        self.assertPosition(nodes[0].op_pos[0], (3, 1), (3, 4), (3, 4))
        self.assertPosition(nodes[0].op_pos[1], (3, 7), (3, 9), (3, 9))
        self.assertPosition(nodes[0].op_pos[2], (4, 1), (4, 3), (4, 3))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_comprehension2(self):
        code = ("#bla\n"
                "[x\n"
                " for x in l\n"
                " if x - 2\n"
                " if x]")
        nodes = get_nodes(code, ast.comprehension)
        self.assertPosition(nodes[0], (3, 1), (5, 5), (3, 4))
        self.assertPosition(nodes[0].op_pos[0], (3, 1), (3, 4), (3, 4))
        self.assertPosition(nodes[0].op_pos[1], (3, 7), (3, 9), (3, 9))
        self.assertPosition(nodes[0].op_pos[2], (4, 1), (4, 3), (4, 3))
        self.assertPosition(nodes[0].op_pos[3], (5, 1), (5, 3), (5, 3))
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python36
    def test_comprehension3(self):
        code = ("async def f():\n"
                "    [x\n"
                "     async for x in l\n"
                "     if x]")
        nodes = get_nodes(code, ast.comprehension)
        self.assertPosition(nodes[0], (3, 5), (4, 9), (3, 14))
        self.assertPosition(nodes[0].op_pos[0], (3, 5), (3, 14), (3, 14))
        self.assertPosition(nodes[0].op_pos[1], (3, 17), (3, 19), (3, 19))
        self.assertPosition(nodes[0].op_pos[2], (4, 5), (4, 7), (4, 7))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_comprehension4(self):
        code = ("#bla\n"
                "[(x)for(x)in(l)if(x)]\n"
                "[(y)for(y)in(m)if(y)]")
        nodes = get_nodes(code, ast.comprehension)
        self.assertPosition(nodes[0], (2, 4), (2, 20), (2, 7))
        self.assertPosition(nodes[0].op_pos[0], (2, 4), (2, 7), (2, 7))
        self.assertPosition(nodes[0].op_pos[1], (2, 10), (2, 12), (2, 12))
        self.assertPosition(nodes[0].op_pos[2], (2, 15), (2, 17), (2, 17))
        self.assertNoBeforeInnerAfter(nodes[0])
        self.assertPosition(nodes[1], (3, 4), (3, 20), (3, 7))
        self.assertPosition(nodes[1].op_pos[0], (3, 4), (3, 7), (3, 7))
        self.assertPosition(nodes[1].op_pos[1], (3, 10), (3, 12), (3, 12))
        self.assertPosition(nodes[1].op_pos[2], (3, 15), (3, 17), (3, 17))
        self.assertNoBeforeInnerAfter(nodes[1])

    @only_python3
    def test_arg(self):
        code = ("#bla\n"
                "def f(x: 'a', y):\n"
                "    pass")
        nodes = get_nodes(code, ast.arg)
        self.assertPosition(nodes[0], (2, 6), (2, 12), (2, 12))
        self.assertPosition(nodes[0].op_pos[0], (2, 7), (2, 8), (2, 8))
        self.assertNoBeforeInnerAfter(nodes[0])
        self.assertPosition(nodes[1], (2, 14), (2, 15), (2, 15))
        self.assertNoBeforeInnerAfter(nodes[1])

    def test_arguments(self):
        code = ("#bla\n"
                "lambda x, y=2, *z, **w : x")
        nodes = get_nodes(code, ast.arguments)
        self.assertPosition(nodes[0], (2, 7), (2, 22), (2, 22))
        self.assertPosition(nodes[0].op_pos[0], (2, 8), (2, 9), (2, 9))
        self.assertPosition(nodes[0].op_pos[1], (2, 11), (2, 12), (2, 12))
        self.assertPosition(nodes[0].op_pos[2], (2, 13), (2, 14), (2, 14))
        self.assertPosition(nodes[0].op_pos[3], (2, 15), (2, 16), (2, 16))
        self.assertPosition(nodes[0].op_pos[4], (2, 17), (2, 18), (2, 18))
        self.assertPosition(nodes[0].op_pos[5], (2, 19), (2, 21), (2, 21))
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python3
    def test_arguments2(self):
        code = ("#bla\n"
                "lambda x, *, y=2: x")
        nodes = get_nodes(code, ast.arguments)
        self.assertPosition(nodes[0], (2, 7), (2, 16), (2, 16))
        self.assertPosition(nodes[0].op_pos[0], (2, 8), (2, 9), (2, 9))
        self.assertPosition(nodes[0].op_pos[1], (2, 10), (2, 11), (2, 11))
        self.assertPosition(nodes[0].op_pos[2], (2, 11), (2, 12), (2, 12))
        self.assertPosition(nodes[0].op_pos[3], (2, 14), (2, 15), (2, 15))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_arguments3(self):
        code = ("#bla\n"
                "lambda  : 2")
        nodes = get_nodes(code, ast.arguments)
        self.assertPosition(nodes[0], (2, 8), (2, 8), (2, 8))
        self.assertEqual(len(nodes[0].op_pos), 0)
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_arguments4(self):
        code = ("#bla\n"
                "def f( x, y=2, *z, **w ):\n"
                "    x")
        nodes = get_nodes(code, ast.arguments)
        self.assertPosition(nodes[0], (2, 7), (2, 22), (2, 22))
        self.assertPosition(nodes[0].op_pos[0], (2, 8), (2, 9), (2, 9))
        self.assertPosition(nodes[0].op_pos[1], (2, 11), (2, 12), (2, 12))
        self.assertPosition(nodes[0].op_pos[2], (2, 13), (2, 14), (2, 14))
        self.assertPosition(nodes[0].op_pos[3], (2, 15), (2, 16), (2, 16))
        self.assertPosition(nodes[0].op_pos[4], (2, 17), (2, 18), (2, 18))
        self.assertPosition(nodes[0].op_pos[5], (2, 19), (2, 21), (2, 21))
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python3
    def test_arguments5(self):
        code = ("#bla\n"
                "def f(x, *, y=2): x")
        nodes = get_nodes(code, ast.arguments)
        self.assertPosition(nodes[0], (2, 6), (2, 15), (2, 15))
        self.assertPosition(nodes[0].op_pos[0], (2, 7), (2, 8), (2, 8))
        self.assertPosition(nodes[0].op_pos[1], (2, 9), (2, 10), (2, 10))
        self.assertPosition(nodes[0].op_pos[2], (2, 10), (2, 11), (2, 11))
        self.assertPosition(nodes[0].op_pos[3], (2, 13), (2, 14), (2, 14))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_arguments6(self):
        code = ("#bla\n"
                "def f(  ):\n"
                "   2")
        nodes = get_nodes(code, ast.arguments)
        self.assertPosition(nodes[0], (2, 8), (2, 8), (2, 8))
        self.assertEqual(len(nodes[0].op_pos), 0)
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_arguments7(self):
        code = ("#bla\n"
                "def f():\n"
                "   2")
        nodes = get_nodes(code, ast.arguments)
        self.assertPosition(nodes[0], (2, 6), (2, 6), (2, 6))
        self.assertEqual(len(nodes[0].op_pos), 0)
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python3
    def test_arguments8(self):
        code = ("#bla\n"
                "def f(x, *, y, z=2): x")
        nodes = get_nodes(code, ast.arguments)
        self.assertPosition(nodes[0], (2, 6), (2, 18), (2, 18))
        self.assertPosition(nodes[0].op_pos[0], (2, 7), (2, 8), (2, 8))
        self.assertPosition(nodes[0].op_pos[1], (2, 9), (2, 10), (2, 10))
        self.assertPosition(nodes[0].op_pos[2], (2, 10), (2, 11), (2, 11))
        self.assertPosition(nodes[0].op_pos[3], (2, 13), (2, 14), (2, 14))
        self.assertPosition(nodes[0].op_pos[4], (2, 16), (2, 17), (2, 17))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_invert(self):
        code = ("#bla\n"
                "~a")
        nodes = get_nodes(code, ast.UnaryOp)
        op = nodes[0].op_pos[0]
        self.assertPosition(op, (2, 0), (2, 1), (2, 1))
        self.assertNoBeforeInnerAfter(op)

    def test_not(self):
        code = ("#bla\n"
                "not a")
        nodes = get_nodes(code, ast.UnaryOp)
        op = nodes[0].op_pos[0]
        self.assertPosition(op, (2, 0), (2, 3), (2, 3))
        self.assertNoBeforeInnerAfter(op)

    def test_usub(self):
        code = ("#bla\n"
                "-a")
        nodes = get_nodes(code, ast.UnaryOp)
        op = nodes[0].op_pos[0]
        self.assertPosition(op, (2, 0), (2, 1), (2, 1))
        self.assertNoBeforeInnerAfter(op)

    def test_uadd(self):
        code = ("#bla\n"
                "+a")
        nodes = get_nodes(code, ast.UnaryOp)
        op = nodes[0].op_pos[0]
        self.assertPosition(op, (2, 0), (2, 1), (2, 1))
        self.assertNoBeforeInnerAfter(op)

    def test_add(self):
        code = ("#bla\n"
                "a + a")
        nodes = get_nodes(code, ast.BinOp)
        op = nodes[0].op_pos[0]
        self.assertPosition(op, (2, 2), (2, 3), (2, 3))
        self.assertNoBeforeInnerAfter(op)

    def test_sub(self):
        code = ("#bla\n"
                "a - a")
        nodes = get_nodes(code, ast.BinOp)
        op = nodes[0].op_pos[0]
        self.assertPosition(op, (2, 2), (2, 3), (2, 3))
        self.assertNoBeforeInnerAfter(op)

    def test_mult(self):
        code = ("#bla\n"
                "a * a")
        nodes = get_nodes(code, ast.BinOp)
        op = nodes[0].op_pos[0]
        self.assertPosition(op, (2, 2), (2, 3), (2, 3))
        self.assertNoBeforeInnerAfter(op)

    @only_python35
    def test_matmult(self):
        code = ("#bla\n"
                "a @ a")
        nodes = get_nodes(code, ast.BinOp)
        op = nodes[0].op_pos[0]
        self.assertPosition(op, (2, 2), (2, 3), (2, 3))
        self.assertNoBeforeInnerAfter(op)

    def test_div(self):
        code = ("#bla\n"
                "a / a")
        nodes = get_nodes(code, ast.BinOp)
        op = nodes[0].op_pos[0]
        self.assertPosition(op, (2, 2), (2, 3), (2, 3))
        self.assertNoBeforeInnerAfter(op)

    def test_mod(self):
        code = ("#bla\n"
                "a % a")
        nodes = get_nodes(code, ast.BinOp)
        op = nodes[0].op_pos[0]
        self.assertPosition(op, (2, 2), (2, 3), (2, 3))
        self.assertNoBeforeInnerAfter(op)

    def test_pow(self):
        code = ("#bla\n"
                "a ** a")
        nodes = get_nodes(code, ast.BinOp)
        op = nodes[0].op_pos[0]
        self.assertPosition(op, (2, 2), (2, 4), (2, 4))
        self.assertNoBeforeInnerAfter(op)

    def test_lshift(self):
        code = ("#bla\n"
                "a << a")
        nodes = get_nodes(code, ast.BinOp)
        op = nodes[0].op_pos[0]
        self.assertPosition(op, (2, 2), (2, 4), (2, 4))
        self.assertNoBeforeInnerAfter(op)

    def test_rshift(self):
        code = ("#bla\n"
                "a >> a")
        nodes = get_nodes(code, ast.BinOp)
        op = nodes[0].op_pos[0]
        self.assertPosition(op, (2, 2), (2, 4), (2, 4))
        self.assertNoBeforeInnerAfter(op)

    def test_bitor(self):
        code = ("#bla\n"
                "a | a")
        nodes = get_nodes(code, ast.BinOp)
        op = nodes[0].op_pos[0]
        self.assertPosition(op, (2, 2), (2, 3), (2, 3))
        self.assertNoBeforeInnerAfter(op)

    def test_bitand(self):
        code = ("#bla\n"
                "a & a")
        nodes = get_nodes(code, ast.BinOp)
        op = nodes[0].op_pos[0]
        self.assertPosition(op, (2, 2), (2, 3), (2, 3))
        self.assertNoBeforeInnerAfter(op)

    def test_floordiv(self):
        code = ("#bla\n"
                "a // a")
        nodes = get_nodes(code, ast.BinOp)
        op = nodes[0].op_pos[0]
        self.assertPosition(op, (2, 2), (2, 4), (2, 4))
        self.assertNoBeforeInnerAfter(op)

    def test_and(self):
        code = ("#bla\n"
                "a and b")
        nodes = get_nodes(code, ast.BoolOp)
        op = nodes[0].op_pos[0]
        self.assertPosition(op, (2, 2), (2, 5), (2, 5))
        self.assertNoBeforeInnerAfter(op)

    def test_or(self):
        code = ("#bla\n"
                "a or b")
        nodes = get_nodes(code, ast.BoolOp)
        op = nodes[0].op_pos[0]
        self.assertPosition(op, (2, 2), (2, 4), (2, 4))
        self.assertNoBeforeInnerAfter(op)

    def test_alias(self):
        code = ("#bla\n"
                "import a,\\\n"
                "b as c")
        nodes = get_nodes(code, ast.alias)
        self.assertPosition(nodes[0], (2, 7), (2, 8), (2, 8))
        self.assertEqual(len(nodes[0].op_pos), 0)
        self.assertNoBeforeInnerAfter(nodes[0])
        self.assertPosition(nodes[1], (3, 0), (3, 6), (3, 6))
        self.assertPosition(nodes[1].op_pos[0], (3, 2), (3, 4), (3, 4))
        self.assertNoBeforeInnerAfter(nodes[1])

    def test_excepthandler(self):
        code = ("#bla\n"
                "try:\n"
                "    a\n"
                "except Exception1:\n"
                "    b\n"
                "except Exception2:\n"
                "    c")
        nodes = get_nodes(code, ast.excepthandler)
        self.assertPosition(nodes[0], (4, 0), (5, 5), (4, 6))
        self.assertPosition(nodes[0].op_pos[0], (4, 0), (4, 6), (4, 6))
        self.assertPosition(nodes[0].op_pos[1], (4, 17), (4, 18), (4, 18))
        self.assertNoBeforeInnerAfter(nodes[0])
        self.assertPosition(nodes[1], (6, 0), (7, 5), (6, 6))
        self.assertPosition(nodes[1].op_pos[0], (6, 0), (6, 6), (6, 6))
        self.assertPosition(nodes[1].op_pos[1], (6, 17), (6, 18), (6, 18))
        self.assertNoBeforeInnerAfter(nodes[1])

    @only_python2
    def test_excepthandler2(self):
        code = ("#bla\n"
                "try:\n"
                "    a\n"
                "except Exception1, target:\n"
                "    b")
        nodes = get_nodes(code, ast.excepthandler)
        self.assertPosition(nodes[0], (4, 0), (5, 5), (4, 6))
        self.assertPosition(nodes[0].op_pos[0], (4, 0), (4, 6), (4, 6))
        self.assertPosition(nodes[0].op_pos[1], (4, 17), (4, 18), (4, 18))
        self.assertPosition(nodes[0].op_pos[2], (4, 25), (4, 26), (4, 26))
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python2
    def test_excepthandler3(self):
        code = ("#bla\n"
                "try:\n"
                "    a\n"
                "except (Exception1, Exception2), target:\n"
                "    b")
        nodes = get_nodes(code, ast.excepthandler)
        self.assertPosition(nodes[0], (4, 0), (5, 5), (4, 6))
        self.assertPosition(nodes[0].op_pos[0], (4, 0), (4, 6), (4, 6))
        self.assertPosition(nodes[0].op_pos[1], (4, 31), (4, 32), (4, 32))
        self.assertPosition(nodes[0].op_pos[2], (4, 39), (4, 40), (4, 40))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_excepthandler4(self):
        code = ("#bla\n"
                "try:\n"
                "    a\n"
                "except Exception1 as target:\n"
                "    b")
        nodes = get_nodes(code, ast.excepthandler)
        self.assertPosition(nodes[0], (4, 0), (5, 5), (4, 6))
        self.assertPosition(nodes[0].op_pos[0], (4, 0), (4, 6), (4, 6))
        self.assertPosition(nodes[0].op_pos[1], (4, 18), (4, 20), (4, 20))
        self.assertPosition(nodes[0].op_pos[2], (4, 27), (4, 28), (4, 28))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_excepthandler5(self):
        code = ("#bla\n"
                "try:\n"
                "    a\n"
                "except (Exception1, Exception2) as target:\n"
                "    b")
        nodes = get_nodes(code, ast.excepthandler)
        self.assertPosition(nodes[0], (4, 0), (5, 5), (4, 6))
        self.assertPosition(nodes[0].op_pos[0], (4, 0), (4, 6), (4, 6))
        self.assertPosition(nodes[0].op_pos[1], (4, 32), (4, 34), (4, 34))
        self.assertPosition(nodes[0].op_pos[2], (4, 41), (4, 42), (4, 42))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_excepthandler6(self):
        code = ("#bla\n"
                "try:\n"
                "    a\n"
                "except(Exception1):\n"
                "    b\n"
                "except(Exception2):\n"
                "    c")
        nodes = get_nodes(code, ast.excepthandler)
        self.assertPosition(nodes[0], (4, 0), (5, 5), (4, 6))
        self.assertPosition(nodes[0].op_pos[0], (4, 0), (4, 6), (4, 6))
        self.assertPosition(nodes[0].op_pos[1], (4, 18), (4, 19), (4, 19))
        self.assertNoBeforeInnerAfter(nodes[0])
        self.assertPosition(nodes[1], (6, 0), (7, 5), (6, 6))
        self.assertPosition(nodes[1].op_pos[0], (6, 0), (6, 6), (6, 6))
        self.assertPosition(nodes[1].op_pos[1], (6, 18), (6, 19), (6, 19))
        self.assertNoBeforeInnerAfter(nodes[1])


    @only_python3
    def test_withitem(self):
        code = ("#bla\n"
                "with x as a, y:\n"
                "    a")
        nodes = get_nodes(code, ast.withitem)
        self.assertPosition(nodes[0], (2, 5), (2, 11), (2, 6))
        self.assertPosition(nodes[0].op_pos[0], (2, 7), (2, 9), (2, 9))
        self.assertNoBeforeInnerAfter(nodes[0])
        self.assertPosition(nodes[1], (2, 13), (2, 14), (2, 14))
        self.assertEqual(len(nodes[1].op_pos), 0)
        self.assertNoBeforeInnerAfter(nodes[1])

    @only_python3
    def test_keyword(self):
        code = ("#bla\n"
                "@dec1\n"
                "class a(metaclass=object):\n"
                "    pass")
        nodes = get_nodes(code, ast.keyword)
        self.assertPosition(nodes[0], (3, 8), (3, 24), (3, 18))
        self.assertPosition(nodes[0].op_pos[0], (3, 17), (3, 18), (3, 18))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_keyword2(self):
        code = ("#bla\n"
                "f(a=2)")
        nodes = get_nodes(code, ast.keyword)
        self.assertPosition(nodes[0], (2, 2), (2, 5), (2, 4))
        self.assertPosition(nodes[0].op_pos[0], (2, 3), (2, 4), (2, 4))
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python35
    def test_keyword3(self):
        code = ("#bla\n"
                "f(x, a=2, **b, ** c)")
        nodes = get_nodes(code, ast.keyword)
        self.assertPosition(nodes[0], (2, 5), (2, 8), (2, 7))
        self.assertPosition(nodes[0].op_pos[0], (2, 6), (2, 7), (2, 7))
        self.assertNoBeforeInnerAfter(nodes[0])
        self.assertPosition(nodes[1], (2, 10), (2, 13), (2, 12))
        self.assertPosition(nodes[1].op_pos[0], (2, 10), (2, 12), (2, 12))
        self.assertNoBeforeInnerAfter(nodes[1])
        self.assertPosition(nodes[2], (2, 15), (2, 19), (2, 17))
        self.assertPosition(nodes[2].op_pos[0], (2, 15), (2, 17), (2, 17))
        self.assertNoBeforeInnerAfter(nodes[2])
