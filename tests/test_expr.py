# Copyright (c) 2015 Universidade Federal Fluminense (UFF)
# This file is part of PyPosAST.
# Please, consult the license terms in the LICENSE file.

from __future__ import (absolute_import, division)

import ast

from .utils import get_nodes, NodeTestCase, only_python2, only_python3


class TestExpr(NodeTestCase):

    def test_name(self):
        code = ("#bla\n"
                "abc")
        nodes = get_nodes(code, ast.Name)
        self.assertPosition(nodes[0], (2, 0), (2, 3), (2, 3))

    def test_name2(self):
        code = ("#bla\n"
                "(z)")
        nodes = get_nodes(code, ast.Name)
        self.assertPosition(nodes[0], (2, 0), (2, 3), (2, 3))

    def test_name3(self):
        code = ("#bla\n"
                "( z )")
        nodes = get_nodes(code, ast.Name)
        self.assertPosition(nodes[0], (2, 0), (2, 5), (2, 5))

    def test_name4(self):
        code = ("#bla\n"
                "((z))")
        nodes = get_nodes(code, ast.Name)
        self.assertPosition(nodes[0], (2, 0), (2, 5), (2, 5))

    def test_name5(self):
        code = ("#bla\n"
                "((z\n"
                "))")
        nodes = get_nodes(code, ast.Name)
        self.assertPosition(nodes[0], (2, 0), (3, 2), (3, 2))

    def test_num(self):
        code = ("#bla\n"
                "12")
        nodes = get_nodes(code, ast.Num)
        self.assertPosition(nodes[0], (2, 0), (2, 2), (2, 2))

    @only_python2
    def test_num2(self):
        """ Python 3 Num uses the minus as unaryop, USub """
        code = ("#bla\n"
                "-  1245")
        nodes = get_nodes(code, ast.Num)
        self.assertPosition(nodes[0], (2, 0), (2, 7), (2, 7))

    @only_python2
    def test_num3(self):
        """ Python 3 Num uses the minus as unaryop, USub """
        code = ("#bla\n"
                "-  0")
        nodes = get_nodes(code, ast.Num)
        self.assertPosition(nodes[0], (2, 0), (2, 4), (2, 4))

    def test_num4(self):
        code = ("#bla\n"
                "0x1245")
        nodes = get_nodes(code, ast.Num)
        self.assertPosition(nodes[0], (2, 0), (2, 6), (2, 6))

    def test_num5(self):
        code = ("#bla\n"
                "(2)")
        nodes = get_nodes(code, ast.Num)
        self.assertPosition(nodes[0], (2, 0), (2, 3), (2, 3))

    def test_num6(self):
        code = ("#bla\n"
                "f(2)")
        nodes = get_nodes(code, ast.Num)
        self.assertPosition(nodes[0], (2, 2), (2, 3), (2, 3))

    def test_str(self):
        code = ("#bla\n"
                "'ab\\\n"
                " cd\\\n"
                " ef'")
        nodes = get_nodes(code, ast.Str)
        self.assertPosition(nodes[0], (2, 0), (4, 4), (4, 4))

    def test_str2(self):
        code = ("#bla\n"
                "'abcd'")
        nodes = get_nodes(code, ast.Str)
        self.assertPosition(nodes[0], (2, 0), (2, 6), (2, 6))

    def test_str3(self):
        code = ("#bla\n"
                "('ab'\\\n"
                " 'cd'\n"
                " 'ef')")
        nodes = get_nodes(code, ast.Str)
        self.assertPosition(nodes[0], (2, 0), (4, 6), (4, 6))

    def test_str4(self):
        code = ("#bla\n"
                "'ab' 'cd' 'ef'")
        nodes = get_nodes(code, ast.Str)
        self.assertPosition(nodes[0], (2, 0), (2, 14), (2, 14))

    def test_attribute(self):
        code = ("#bla\n"
                "a.b")
        nodes = get_nodes(code, ast.Attribute)
        self.assertPosition(nodes[0], (2, 0), (2, 3), (2, 1))

    def test_attribute2(self):
        code = ("#bla\n"
                "a.\\\n"
                "b")
        nodes = get_nodes(code, ast.Attribute)
        self.assertPosition(nodes[0], (2, 0), (3, 1), (2, 1))

    def test_attribute3(self):
        code = ("#bla\n"
                "a.b.c")
        nodes = get_nodes(code, ast.Attribute)
        self.assertPosition(nodes[0], (2, 0), (2, 5), (2, 3))
        self.assertPosition(nodes[1], (2, 0), (2, 3), (2, 1))

    def test_attribute4(self):
        code = ("#bla\n"
                "a.\\\n"
                "b.c\\\n"
                ".d")
        nodes = get_nodes(code, ast.Attribute)
        self.assertPosition(nodes[0], (2, 0), (4, 2), (4, 0))
        self.assertPosition(nodes[1], (2, 0), (3, 3), (3, 1))
        self.assertPosition(nodes[2], (2, 0), (3, 1), (2, 1))

    def test_attribute5(self):
        code = ("#bla\n"
                "(a.\\\n"
                "   b)")
        nodes = get_nodes(code, ast.Attribute)
        self.assertPosition(nodes[0], (2, 0), (3, 5), (2, 2))

    def test_ellipsis(self):
        code = ("#bla\n"
                "a[...]")
        nodes = get_nodes(code, ast.Ellipsis)
        self.assertPosition(nodes[0], (2, 2), (2, 5), (2, 5))

    @only_python2
    def test_ellipsis2(self):
        """ Invalid Python 3 syntax """
        code = ("#bla\n"
                "a[.\\\n"
                "..]")
        nodes = get_nodes(code, ast.Ellipsis)
        self.assertPosition(nodes[0], (2, 2), (3, 2), (3, 2))

    @only_python3
    def test_ellipsis3(self):
        """ Invalid Python 2 syntax """
        code = ("#bla\n"
                "a[(...)]")
        nodes = get_nodes(code, ast.Ellipsis)
        self.assertPosition(nodes[0], (2, 2), (2, 7), (2, 7))

    def test_subscript(self):
        code = ("#bla\n"
                "a\\\n"
                "[1]")
        nodes = get_nodes(code, ast.Subscript)
        self.assertPosition(nodes[0], (2, 0), (3, 3), (3, 3))

    def test_subscript2(self):
        code = ("#bla\n"
                "a[\n"
                "1]")
        nodes = get_nodes(code, ast.Subscript)
        self.assertPosition(nodes[0], (2, 0), (3, 2), (3, 2))

    def test_subscript3(self):
        code = ("#bla\n"
                "a[1:\n"
                "2,\n"
                "3 ]")
        nodes = get_nodes(code, ast.Subscript)
        self.assertPosition(nodes[0], (2, 0), (4, 3), (4, 3))

    def test_subscript4(self):
        code = ("#bla\n"
                "(a\n"
                "[1])")
        nodes = get_nodes(code, ast.Subscript)
        self.assertPosition(nodes[0], (2, 0), (3, 4), (3, 4))

    def test_tuple(self):
        code = ("#bla\n"
                "(\n"
                "1, 2,\n"
                "3\n"
                ")")
        nodes = get_nodes(code, ast.Tuple)
        self.assertPosition(nodes[0], (2, 0), (5, 1), (3, 1))

    def test_tuple2(self):
        code = ("#bla\n"
                "(\n"
                ")")

        nodes = get_nodes(code, ast.Tuple)
        self.assertPosition(nodes[0], (2, 0), (3, 1), (3, 1))

    def test_tuple3(self):
        code = ("#bla\n"
                "(((0),\n"
                "1, 2,\n"
                "3\n"
                "))")
        nodes = get_nodes(code, ast.Tuple)
        self.assertPosition(nodes[0], (2, 0), (5, 2), (2, 5))

    def test_tuple4(self):
        code = ("#bla\n"
                "1,")
        nodes = get_nodes(code, ast.Tuple)
        self.assertPosition(nodes[0], (2, 0), (2, 1), (2, 1))

    def test_tuple5(self):
        code = ("#bla\n"
                "([1, 2], 3)")
        nodes = get_nodes(code, ast.Tuple)
        self.assertPosition(nodes[0], (2, 0), (2, 11), (2, 7))

    def test_list(self):
        code = ("#bla\n"
                "[\n"
                "1, 2,\n"
                "3\n"
                "]")
        nodes = get_nodes(code, ast.List)
        self.assertPosition(nodes[0], (2, 0), (5, 1), (5, 1))

    def test_list2(self):
        code = ("#bla\n"
                "[\n"
                "]")

        nodes = get_nodes(code, ast.List)
        self.assertPosition(nodes[0], (2, 0), (3, 1), (3, 1))

    def test_list3(self):
        code = ("#bla\n"
                "([(0),\n"
                "1, 2,\n"
                "3\n"
                "])")
        nodes = get_nodes(code, ast.List)
        self.assertPosition(nodes[0], (2, 0), (5, 2), (5, 2))

    @only_python2
    def test_repr(self):
        code = ("#bla\n"
                "`1`")
        nodes = get_nodes(code, ast.Repr)
        self.assertPosition(nodes[0], (2, 0), (2, 3), (2, 3))

    @only_python2
    def test_repr2(self):
        code = ("#bla\n"
                "``1``")
        nodes = get_nodes(code, ast.Repr)
        self.assertPosition(nodes[0], (2, 0), (2, 5), (2, 5))

    @only_python2
    def test_repr3(self):
        code = ("#bla\n"
                "``2\\\n"
                "``")
        nodes = get_nodes(code, ast.Repr)
        self.assertPosition(nodes[0], (2, 0), (3, 2), (3, 2))

    @only_python2
    def test_repr4(self):
        code = ("#bla\n"
                "(``2\n"
                "``)")
        nodes = get_nodes(code, ast.Repr)
        self.assertPosition(nodes[0], (2, 0), (3, 3), (3, 3))

    def test_call(self):
        code = ("#bla\n"
                "fn(\n"
                "2)")
        nodes = get_nodes(code, ast.Call)
        self.assertPosition(nodes[0], (2, 0), (3, 2), (3, 2))

    def test_call2(self):
        code = ("#bla\n"
                "fn(\n"
                "2)")
        nodes = get_nodes(code, ast.Call)
        self.assertPosition(nodes[0], (2, 0), (3, 2), (3, 2))

    def test_call3(self):
        code = ("#bla\n"
                "fn\\\n"
                "((\n"
                "2, 3))")
        nodes = get_nodes(code, ast.Call)
        self.assertPosition(nodes[0], (2, 0), (4, 6), (4, 6))

    def test_call4(self):
        code = ("#bla\n"
                "fn()\\\n"
                "((\n"
                "2, 3))")
        nodes = get_nodes(code, ast.Call)
        self.assertPosition(nodes[0], (2, 0), (4, 6), (4, 6))
        self.assertPosition(nodes[1], (2, 0), (2, 4), (2, 4))

    def test_call5(self):
        code = ("#bla\n"
                "(fn(\n"
                "2))")
        nodes = get_nodes(code, ast.Call)
        self.assertPosition(nodes[0], (2, 0), (3, 3), (3, 3))

    def test_compare(self):
        code = ("#bla\n"
                "2 < 3")
        nodes = get_nodes(code, ast.Compare)
        self.assertPosition(nodes[0], (2, 0), (2, 5), (2, 5))

    def test_compare2(self):
        code = ("#bla\n"
                "2 < 3 <\\\n"
                " 5")
        nodes = get_nodes(code, ast.Compare)
        self.assertPosition(nodes[0], (2, 0), (3, 2), (3, 2))

    def test_compare3(self):
        code = ("#bla\n"
                "(2 < 3 <\n"
                " 5)")
        nodes = get_nodes(code, ast.Compare)
        self.assertPosition(nodes[0], (2, 0), (3, 3), (3, 3))

    def test_yield(self):
        code = ("#bla\n"
                "yield   2")
        nodes = get_nodes(code, ast.Yield)
        self.assertPosition(nodes[0], (2, 0), (2, 9), (2, 5))

    def test_yield2(self):
        code = ("#bla\n"
                "(yield \n"
                "2)")
        nodes = get_nodes(code, ast.Yield)
        self.assertPosition(nodes[0], (2, 0), (3, 2), (2, 6))

    def test_generator_exp(self):
        code = ("#bla\n"
                "f(x\n"
                " for x in l\n"
                " if x)")
        nodes = get_nodes(code, ast.GeneratorExp)
        self.assertPosition(nodes[0], (2, 2), (4, 5), (2, 3))

    def test_dict_comp(self):
        code = ("#bla\n"
                "{x:2\n"
                " for x in l\n"
                " if x}")
        nodes = get_nodes(code, ast.DictComp)
        self.assertPosition(nodes[0], (2, 0), (4, 6), (4, 6))

    def test_dict_comp2(self):
        code = ("#bla\n"
                "({x:2\n"
                " for x in l\n"
                " if x})")
        nodes = get_nodes(code, ast.DictComp)
        self.assertPosition(nodes[0], (2, 0), (4, 7), (4, 7))

    def test_set_comp(self):
        code = ("#bla\n"
                "{x\n"
                " for x in l\n"
                " if x}")
        nodes = get_nodes(code, ast.SetComp)
        self.assertPosition(nodes[0], (2, 0), (4, 6), (4, 6))

    def test_set_comp2(self):
        code = ("#bla\n"
                "({x\n"
                " for x in l\n"
                " if x})")
        nodes = get_nodes(code, ast.SetComp)
        self.assertPosition(nodes[0], (2, 0), (4, 7), (4, 7))

    def test_list_comp(self):
        code = ("#bla\n"
                "[x\n"
                " for x in l\n"
                " if x]")
        nodes = get_nodes(code, ast.ListComp)
        self.assertPosition(nodes[0], (2, 0), (4, 6), (4, 6))

    def test_list_comp2(self):
        code = ("#bla\n"
                "([x\n"
                " for x in l\n"
                " if x])")
        nodes = get_nodes(code, ast.ListComp)
        self.assertPosition(nodes[0], (2, 0), (4, 7), (4, 7))

    def test_set(self):
        code = ("#bla\n"
                "{x,\n"
                " 1,\n"
                " 3}")
        nodes = get_nodes(code, ast.Set)
        self.assertPosition(nodes[0], (2, 0), (4, 3), (4, 3))

    def test_set2(self):
        code = ("#bla\n"
                "({x,\n"
                " 1,\n"
                " 3})")
        nodes = get_nodes(code, ast.Set)
        self.assertPosition(nodes[0], (2, 0), (4, 4), (4, 4))

    def test_dict(self):
        code = ("#bla\n"
                "{}")
        nodes = get_nodes(code, ast.Dict)
        self.assertPosition(nodes[0], (2, 0), (2, 2), (2, 2))

    def test_dict2(self):
        code = ("#bla\n"
                "{1}, {1: x,\n"
                "  2: 1,\n"
                "  3: 3}")
        nodes = get_nodes(code, ast.Dict)
        self.assertPosition(nodes[0], (2, 5), (4, 7), (4, 7))

    def test_dict3(self):
        code = ("#bla\n"
                "{1}, ({1: x,\n"
                "  2: 1,\n"
                "  3: 3})")
        nodes = get_nodes(code, ast.Dict)
        self.assertPosition(nodes[0], (2, 5), (4, 8), (4, 8))

    def test_if_exp(self):
        code = ("#bla\n"
                "1 if 2\\\n"
                "  else 3")
        nodes = get_nodes(code, ast.IfExp)
        self.assertPosition(nodes[0], (2, 0), (3, 8), (2, 4))

    def test_if_exp2(self):
        code = ("#bla\n"
                "(1 if 2\n"
                "  else 3)")
        nodes = get_nodes(code, ast.IfExp)
        self.assertPosition(nodes[0], (2, 0), (3, 9), (2, 5))

    def test_lambda(self):
        code = ("#bla\n"
                "lambda x, y:\\\n"
                "x")
        nodes = get_nodes(code, ast.Lambda)
        self.assertPosition(nodes[0], (2, 0), (3, 1), (2, 12))

    def test_lambda2(self):
        code = ("#bla\n"
                "(lambda x, y:\n"
                "x)")
        nodes = get_nodes(code, ast.Lambda)
        self.assertPosition(nodes[0], (2, 0), (3, 2), (2, 13))

    def test_unary_op(self):
        code = ("#bla\n"
                "- a")
        nodes = get_nodes(code, ast.UnaryOp)
        self.assertPosition(nodes[0], (2, 0), (2, 3), (2, 1))

    def test_unary_op2(self):
        code = ("#bla\n"
                "(-\n"
                "a)")
        nodes = get_nodes(code, ast.UnaryOp)
        self.assertPosition(nodes[0], (2, 0), (3, 2), (2, 2))

    def test_binop(self):
        code = ("#bla\n"
                "ab+a")
        nodes = get_nodes(code, ast.BinOp)
        self.assertPosition(nodes[0], (2, 0), (2, 4), (2, 3))

    def test_binop2(self):
        code = ("#bla\n"
                "a * b + c")
        nodes = get_nodes(code, ast.BinOp)
        self.assertPosition(nodes[0], (2, 0), (2, 9), (2, 7))
        self.assertPosition(nodes[1], (2, 0), (2, 5), (2, 3))

    def test_binop3(self):
        code = ("#bla\n"
                "(b + a)")
        nodes = get_nodes(code, ast.BinOp)
        self.assertPosition(nodes[0], (2, 0), (2, 7), (2, 4))

    def test_bool_op(self):
        code = ("#bla\n"
                "a and b and c")
        nodes = get_nodes(code, ast.BoolOp)
        self.assertPosition(nodes[0], (2, 0), (2, 13), (2, 13))

    def test_bool_op2(self):
        code = ("#bla\n"
                "a and b or c")
        nodes = get_nodes(code, ast.BoolOp)
        self.assertPosition(nodes[0], (2, 0), (2, 12), (2, 12))
        self.assertPosition(nodes[1], (2, 0), (2, 7), (2, 7))

    def test_bool_op3(self):
        code = ("#bla\n"
                "(a and b and c)")
        nodes = get_nodes(code, ast.BoolOp)
        self.assertPosition(nodes[0], (2, 0), (2, 15), (2, 15))

    @only_python3
    def test_starred(self):
        code = ("#bla\n"
                "a, * b = 1, 2, 3")
        nodes = get_nodes(code, ast.Starred)
        self.assertPosition(nodes[0], (2, 3), (2, 6), (2, 4))

    @only_python3
    def test_starred2(self):
        code = ("#bla\n"
                "a, (* b) = 1, 2, 3")
        nodes = get_nodes(code, ast.Starred)
        self.assertPosition(nodes[0], (2, 3), (2, 8), (2, 5))

    @only_python3
    def test_name_constant(self):
        code = ("#bla\n"
                "None")
        nodes = get_nodes(code, ast.NameConstant)
        self.assertPosition(nodes[0], (2, 0), (2, 4), (2, 4))

    @only_python3
    def test_name_constant2(self):
        code = ("#bla\n"
                "True")
        nodes = get_nodes(code, ast.NameConstant)
        self.assertPosition(nodes[0], (2, 0), (2, 4), (2, 4))

    @only_python3
    def test_name_constant3(self):
        code = ("#bla\n"
                "False")
        nodes = get_nodes(code, ast.NameConstant)
        self.assertPosition(nodes[0], (2, 0), (2, 5), (2, 5))

    @only_python3
    def test_name_constant4(self):
        code = ("#bla\n"
                "(None)")
        nodes = get_nodes(code, ast.NameConstant)
        self.assertPosition(nodes[0], (2, 0), (2, 6), (2, 6))

    @only_python3
    def test_bytes(self):
        code = ("#bla\n"
                "b'ab\\\n"
                " cd\\\n"
                " ef'")
        nodes = get_nodes(code, ast.Bytes)
        self.assertPosition(nodes[0], (2, 0), (4, 4), (4, 4))

    @only_python3
    def test_bytes2(self):
        code = ("#bla\n"
                "b'abcd'")
        nodes = get_nodes(code, ast.Bytes)
        self.assertPosition(nodes[0], (2, 0), (2, 7), (2, 7))

    @only_python3
    def test_bytes3(self):
        code = ("#bla\n"
                "(b'ab'\\\n"
                " b'cd'\n"
                " b'ef')")
        nodes = get_nodes(code, ast.Bytes)
        self.assertPosition(nodes[0], (2, 0), (4, 7), (4, 7))

    @only_python3
    def test_bytes4(self):
        code = ("#bla\n"
                "b'ab' b'cd' b'ef'")
        nodes = get_nodes(code, ast.Bytes)
        self.assertPosition(nodes[0], (2, 0), (2, 17), (2, 17))

    @only_python3
    def test_yield_from(self):
        code = ("#bla\n"
                "yield from  2")
        nodes = get_nodes(code, ast.YieldFrom)
        self.assertPosition(nodes[0], (2, 0), (2, 13), (2, 10))

    @only_python3
    def test_yield_from2(self):
        code = ("#bla\n"
                "yield  \\\n"
                " from  2")
        nodes = get_nodes(code, ast.YieldFrom)
        self.assertPosition(nodes[0], (2, 0), (3, 8), (3, 5))

    @only_python3
    def test_yield_from3(self):
        code = ("#bla\n"
                "(yield  \n"
                "from  2)")
        nodes = get_nodes(code, ast.YieldFrom)
        self.assertPosition(nodes[0], (2, 0), (3, 8), (3, 4))
