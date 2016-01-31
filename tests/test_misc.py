# Copyright (c) 2016 Universidade Federal Fluminense (UFF)
# This file is part of PyPosAST.
# Please, consult the license terms in the LICENSE file.

from __future__ import (absolute_import, division)

import ast

from .utils import get_nodes, NodeTestCase
from .utils import only_python2, only_python3, only_python35


class TestMisc(NodeTestCase):

    def test_index(self):
        code = ("#bla\n"
                "a[1]")
        nodes = get_nodes(code, ast.Index)
        self.assertPosition(nodes[0], (2, 2), (2, 3), (2, 3))

    def test_slice(self):
        code = ("#bla\n"
                "a[1:2:3]")
        nodes = get_nodes(code, ast.Slice)
        self.assertPosition(nodes[0], (2, 2), (2, 7), (2, 4))

    def test_slice2(self):
        code = ("#bla\n"
                "a[:\\\n"
                "2:3]")
        nodes = get_nodes(code, ast.Slice)
        self.assertPosition(nodes[0], (2, 2), (3, 3), (2, 3))

    def test_slice3(self):
        code = ("#bla\n"
                "a[:\\\n"
                ":2]")
        nodes = get_nodes(code, ast.Slice)
        self.assertPosition(nodes[0], (2, 2), (3, 2), (2, 3))

    def test_slice4(self):
        code = ("#bla\n"
                "a[:]")
        nodes = get_nodes(code, ast.Slice)
        self.assertPosition(nodes[0], (2, 2), (2, 3), (2, 3))

    def test_slice5(self):
        code = ("#bla\n"
                "a[::]")
        nodes = get_nodes(code, ast.Slice)
        self.assertPosition(nodes[0], (2, 2), (2, 4), (2, 3))

    def test_slice6(self):
        code = ("#bla\n"
                "a[11:2\\\n"
                ":]")
        nodes = get_nodes(code, ast.Slice)
        self.assertPosition(nodes[0], (2, 2), (3, 1), (2, 5))

    def test_slice7(self):
        code = ("#bla\n"
                "a[::None]")
        nodes = get_nodes(code, ast.Slice)
        self.assertPosition(nodes[0], (2, 2), (2, 8), (2, 3))

    def test_ext_slice(self):
        code = ("#bla\n"
                "a[1:2,3]")
        nodes = get_nodes(code, ast.ExtSlice)
        self.assertPosition(nodes[0], (2, 2), (2, 7), (2, 6))

    def test_ext_slice2(self):
        code = ("#bla\n"
                "a[1:2:,3]")
        nodes = get_nodes(code, ast.ExtSlice)
        self.assertPosition(nodes[0], (2, 2), (2, 8), (2, 7))

    def test_ext_slice2(self):
        code = ("#bla\n"
                "a[3,1:2:]")
        nodes = get_nodes(code, ast.ExtSlice)
        self.assertPosition(nodes[0], (2, 2), (2, 8), (2, 4))

    def test_eq(self):
        code = ("#bla\n"
                "2 == 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertPosition(comp, (2, 2), (2, 4), (2, 4))

    def test_not_eq(self):
        code = ("#bla\n"
                "2 != 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertPosition(comp, (2, 2), (2, 4), (2, 4))

    def test_not_eq2(self):
        """ Python 2 syntax """
        code = ("#bla\n"
                "2 != 4\n"
                "5 != 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertPosition(comp, (2, 2), (2, 4), (2, 4))
        comp2 = nodes[1].op_pos[0]
        self.assertPosition(comp2, (3, 2), (3, 4), (3, 4))

    @only_python2
    def test_not_eq3(self):
        """ Python 2 syntax """
        code = ("#bla\n"
                "2 <> 4\n"
                "5 != 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertPosition(comp, (2, 2), (2, 4), (2, 4))
        comp2 = nodes[1].op_pos[0]
        self.assertPosition(comp2, (3, 2), (3, 4), (3, 4))

    def test_lt(self):
        code = ("#bla\n"
                "2 < 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertPosition(comp, (2, 2), (2, 3), (2, 3))

    def test_lte(self):
        code = ("#bla\n"
                "2 <= 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertPosition(comp, (2, 2), (2, 4), (2, 4))

    def test_gt(self):
        code = ("#bla\n"
                "2 > 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertPosition(comp, (2, 2), (2, 3), (2, 3))

    def test_gte(self):
        code = ("#bla\n"
                "2 >= 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertPosition(comp, (2, 2), (2, 4), (2, 4))

    def test_is(self):
        code = ("#bla\n"
                "2 is 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertPosition(comp, (2, 2), (2, 4), (2, 4))

    def test_is_not(self):
        code = ("#bla\n"
                "2 is not 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertPosition(comp, (2, 2), (2, 8), (2, 8))

    def test_in(self):
        code = ("#bla\n"
                "2 in 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertPosition(comp, (2, 2), (2, 4), (2, 4))

    def test_not_in(self):
        code = ("#bla\n"
                "2 not in 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertPosition(comp, (2, 2), (2, 8), (2, 8))

    def test_comprehension(self):
        code = ("#bla\n"
                "[x\n"
                " for x in l\n"
                " if x]")
        nodes = get_nodes(code, ast.comprehension)
        self.assertPosition(nodes[0], (3, 1), (4, 5), (3, 4))

    @only_python3
    def test_arg(self):
        code = ("#bla\n"
                "def f(x: 'a', y):\n"
                "    pass")
        nodes = get_nodes(code, ast.arg)
        self.assertPosition(nodes[0], (2, 6), (2, 12), (2, 12))
        self.assertPosition(nodes[1], (2, 14), (2, 15), (2, 15))

    def test_arguments(self):
        code = ("#bla\n"
                "lambda x, y=2, *z, **w : x")
        nodes = get_nodes(code, ast.arguments)
        self.assertPosition(nodes[0], (2, 7), (2, 22), (2, 22))

    @only_python3
    def test_arguments2(self):
        code = ("#bla\n"
                "lambda x, *, y=2: x")
        nodes = get_nodes(code, ast.arguments)
        self.assertPosition(nodes[0], (2, 7), (2, 16), (2, 16))

    def test_arguments3(self):
        code = ("#bla\n"
                "lambda  : 2")
        nodes = get_nodes(code, ast.arguments)
        self.assertPosition(nodes[0], (2, 8), (2, 8), (2, 8))

    def test_arguments4(self):
        code = ("#bla\n"
                "def f( x, y=2, *z, **w ):\n"
                "    x")
        nodes = get_nodes(code, ast.arguments)
        self.assertPosition(nodes[0], (2, 7), (2, 22), (2, 22))

    @only_python3
    def test_arguments5(self):
        code = ("#bla\n"
                "def f(x, *, y=2): x")
        nodes = get_nodes(code, ast.arguments)
        self.assertPosition(nodes[0], (2, 6), (2, 15), (2, 15))

    def test_arguments6(self):
        code = ("#bla\n"
                "def f(  ):\n"
                "   2")
        nodes = get_nodes(code, ast.arguments)
        self.assertPosition(nodes[0], (2, 8), (2, 8), (2, 8))

    def test_arguments7(self):
        code = ("#bla\n"
                "def f():\n"
                "   2")
        nodes = get_nodes(code, ast.arguments)
        self.assertPosition(nodes[0], (2, 6), (2, 6), (2, 6))


    def test_invert(self):
        code = ("#bla\n"
                "~a")
        nodes = get_nodes(code, ast.UnaryOp)
        op = nodes[0].op_pos
        self.assertPosition(op, (2, 0), (2, 1), (2, 1))

    def test_not(self):
        code = ("#bla\n"
                "not a")
        nodes = get_nodes(code, ast.UnaryOp)
        op = nodes[0].op_pos
        self.assertPosition(op, (2, 0), (2, 3), (2, 3))

    def test_usub(self):
        code = ("#bla\n"
                "-a")
        nodes = get_nodes(code, ast.UnaryOp)
        op = nodes[0].op_pos
        self.assertPosition(op, (2, 0), (2, 1), (2, 1))

    def test_uadd(self):
        code = ("#bla\n"
                "+a")
        nodes = get_nodes(code, ast.UnaryOp)
        op = nodes[0].op_pos
        self.assertPosition(op, (2, 0), (2, 1), (2, 1))

    def test_add(self):
        code = ("#bla\n"
                "a + a")
        nodes = get_nodes(code, ast.BinOp)
        op = nodes[0].op_pos
        self.assertPosition(op, (2, 2), (2, 3), (2, 3))

    def test_sub(self):
        code = ("#bla\n"
                "a - a")
        nodes = get_nodes(code, ast.BinOp)
        op = nodes[0].op_pos
        self.assertPosition(op, (2, 2), (2, 3), (2, 3))

    def test_mult(self):
        code = ("#bla\n"
                "a * a")
        nodes = get_nodes(code, ast.BinOp)
        op = nodes[0].op_pos
        self.assertPosition(op, (2, 2), (2, 3), (2, 3))

    @only_python35
    def test_matmult(self):
        code = ("#bla\n"
                "a @ a")
        nodes = get_nodes(code, ast.BinOp)
        op = nodes[0].op_pos
        self.assertPosition(op, (2, 2), (2, 3), (2, 3))

    def test_div(self):
        code = ("#bla\n"
                "a / a")
        nodes = get_nodes(code, ast.BinOp)
        op = nodes[0].op_pos
        self.assertPosition(op, (2, 2), (2, 3), (2, 3))

    def test_mod(self):
        code = ("#bla\n"
                "a % a")
        nodes = get_nodes(code, ast.BinOp)
        op = nodes[0].op_pos
        self.assertPosition(op, (2, 2), (2, 3), (2, 3))

    def test_pow(self):
        code = ("#bla\n"
                "a ** a")
        nodes = get_nodes(code, ast.BinOp)
        op = nodes[0].op_pos
        self.assertPosition(op, (2, 2), (2, 4), (2, 4))

    def test_lshift(self):
        code = ("#bla\n"
                "a << a")
        nodes = get_nodes(code, ast.BinOp)
        op = nodes[0].op_pos
        self.assertPosition(op, (2, 2), (2, 4), (2, 4))

    def test_rshift(self):
        code = ("#bla\n"
                "a >> a")
        nodes = get_nodes(code, ast.BinOp)
        op = nodes[0].op_pos
        self.assertPosition(op, (2, 2), (2, 4), (2, 4))

    def test_bitor(self):
        code = ("#bla\n"
                "a | a")
        nodes = get_nodes(code, ast.BinOp)
        op = nodes[0].op_pos
        self.assertPosition(op, (2, 2), (2, 3), (2, 3))

    def test_bitand(self):
        code = ("#bla\n"
                "a & a")
        nodes = get_nodes(code, ast.BinOp)
        op = nodes[0].op_pos
        self.assertPosition(op, (2, 2), (2, 3), (2, 3))

    def test_floordiv(self):
        code = ("#bla\n"
                "a // a")
        nodes = get_nodes(code, ast.BinOp)
        op = nodes[0].op_pos
        self.assertPosition(op, (2, 2), (2, 4), (2, 4))

    def test_and(self):
        code = ("#bla\n"
                "a and b")
        nodes = get_nodes(code, ast.BoolOp)
        op = nodes[0].op_pos[0]
        self.assertPosition(op, (2, 2), (2, 5), (2, 5))

    def test_or(self):
        code = ("#bla\n"
                "a or b")
        nodes = get_nodes(code, ast.BoolOp)
        op = nodes[0].op_pos[0]
        self.assertPosition(op, (2, 2), (2, 4), (2, 4))

    def test_alias(self):
        code = ("#bla\n"
                "import a,\\\n"
                "b as c")
        nodes = get_nodes(code, ast.alias)
        self.assertPosition(nodes[0], (2, 7), (2, 8), (2, 8))
        self.assertPosition(nodes[1], (3, 0), (3, 6), (3, 6))

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
        self.assertPosition(nodes[1], (6, 0), (7, 5), (6, 6))

    @only_python3
    def test_withitem(self):
        code = ("#bla\n"
                "with x as a, y:\n"
                "    a")
        nodes = get_nodes(code, ast.withitem)
        self.assertPosition(nodes[0], (2, 5), (2, 11), (2, 6))
        self.assertPosition(nodes[1], (2, 13), (2, 14), (2, 14))

    @only_python3
    def test_keyword(self):
        code = ("#bla\n"
                "@dec1\n"
                "class a(metaclass=object):\n"
                "    pass")
        nodes = get_nodes(code, ast.keyword)
        self.assertPosition(nodes[0], (3, 8), (3, 24), (3, 18))

    def test_keyword2(self):
        code = ("#bla\n"
                "f(a=2)")
        nodes = get_nodes(code, ast.keyword)
        self.assertPosition(nodes[0], (2, 2), (2, 5), (2, 4))

    @only_python35
    def test_keyword3(self):
        code = ("#bla\n"
                "f(x, a=2, **b, ** c)")
        nodes = get_nodes(code, ast.keyword)
        self.assertPosition(nodes[0], (2, 5), (2, 8), (2, 7))
        self.assertPosition(nodes[1], (2, 10), (2, 13), (2, 12))
        self.assertPosition(nodes[2], (2, 15), (2, 19), (2, 17))
