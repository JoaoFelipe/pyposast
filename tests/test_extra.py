# Copyright (c) 2015 Universidade Federal Fluminense (UFF)
# This file is part of PyPosAST.
# Please, consult the license terms in the LICENSE file.

from __future__ import (absolute_import, division)

import ast
import textwrap

from .utils import NodeTestCase
from pyposast import get_nodes


class TestExtra(NodeTestCase):

    def test_noworkflow_var(self):
        code = """
            def x(a=1):
                return a
            for j in range(3):
                for i in range(j):
                    print(i)
                    i = i**2
                    i += 2

            class A():
                pass

            a = x(a=2)
            a = b = c = 1
            a = range(5)
            A.a = c
            a[b] = b
            e = b, c = c, 1
            a, (b, c) = b, e
            a += (lambda b: b)(a)
            b = a
            a = 2
            c = {
                'a': a,
                'b': b
            }
            d = [a, b, c]
            d[1] += 1

            print(a)
            print(b)
            print(c)

            a, b = 1, c
        """
        code = textwrap.dedent(code)
        nodes = get_nodes(code, ast.FunctionDef)
        self.assertPosition(nodes[0], (2, 0), (3, 12), (2, 3))
        nodes = get_nodes(code, ast.For)
        self.assertPosition(nodes[0], (4, 0), (8, 14), (4, 3))
        self.assertPosition(nodes[1], (5, 4), (8, 14), (5, 7))
        nodes = get_nodes(code, ast.ClassDef)
        self.assertPosition(nodes[0], (10, 0), (11, 8), (10, 5))
        nodes = get_nodes(code, ast.Assign)
        self.assertPosition(nodes[0], (7, 8), (7, 16), (7, 16))
        self.assertPosition(nodes[1], (13, 0), (13, 10), (13, 10))
        self.assertPosition(nodes[2], (14, 0), (14, 13), (14, 13))
        self.assertPosition(nodes[3], (15, 0), (15, 12), (15, 12))
        self.assertPosition(nodes[4], (16, 0), (16, 7), (16, 7))
        self.assertPosition(nodes[5], (17, 0), (17, 8), (17, 8))
        self.assertPosition(nodes[6], (18, 0), (18, 15), (18, 15))
        self.assertPosition(nodes[7], (19, 0), (19, 16), (19, 16))
        self.assertPosition(nodes[8], (21, 0), (21, 5), (21, 5))
        self.assertPosition(nodes[9], (22, 0), (22, 5), (22, 5))
        self.assertPosition(nodes[10], (23, 0), (26, 1), (26, 1))
        self.assertPosition(nodes[11], (27, 0), (27, 13), (27, 13))
        self.assertPosition(nodes[12], (34, 0), (34, 11), (34, 11))
        nodes = get_nodes(code, ast.List)
        self.assertPosition(nodes[0], (27, 4), (27, 13), (27, 13))

    def test_update_parenthesis(self):
        code = ("patterns('',\n"
                "    # url(r'^$', 'views.home', name='home')\n"
                "\n"
                "    url(r'^index$', 'views.index', name='index'),\n"
                "    url(r'^root$', 'views.root', name='root'),\n"
                "    # url(r'^$', 'views.home', name='home'),\n"
                ")")
        nodes = get_nodes(code, ast.Call)
        self.assertPosition(nodes[0], (1, 0), (7, 1), (7, 1))
        self.assertPosition(nodes[1], (4, 4), (4, 48), (4, 48))
        self.assertPosition(nodes[2], (5, 4), (5, 45), (5, 45))

    def test_assign_tuple(self):
        code = ("abc.mno = func()\n"
                "abc.pqr.ghi = ()\n"
                "abc.jkl = b''")
        nodes = get_nodes(code, ast.Assign)
        self.assertPosition(nodes[0], (1, 0), (1, 16), (1, 16))
        self.assertPosition(nodes[1], (2, 0), (2, 16), (2, 16))
        self.assertPosition(nodes[2], (3, 0), (3, 13), (3, 13))

    def test_relative_import_and_assign_attribute(self):
        code = ("from ..a import b\n"
                "abc.ghi = [jkl.mno.pqr(name=name) for name in 'abc']")
        nodes = get_nodes(code, ast.Assign)
        self.assertPosition(nodes[0], (2, 0), (2, 52), (2, 52))

    def test_update_parenthesis2(self):
        code = ("a = fn(\n"
                "    b=1,\n"
                "    c=[\n"
                "        c.d(\n"
                "            e='a',\n"
                "            f='b',\n"
                "            g=c,\n"
                "        )\n"
                "    ]\n"
                "\n"
                ")")
        nodes = get_nodes(code, ast.List)
        self.assertPosition(nodes[0], (3, 6), (9, 5), (9, 5))

    def test_attribute(self):
        code = ("(abc.ghi(ijk=[abc.lmn, abc.opq]).\n"
                "    rst('a').uvw('a') |\n"
                " abc.ghi(ijk=[abc.xyz]).\n"
                "    rst('a').uvw('a'),\n"
                " ['b', 'c'],"
                ")")
        nodes = get_nodes(code, ast.Attribute)
        self.assertPosition(nodes[0], (1, 1), (2, 16), (2, 13))
        self.assertPosition(nodes[1], (1, 1), (2, 7), (1, 33))
        self.assertPosition(nodes[2], (1, 1), (1, 8), (1, 5))
        self.assertPosition(nodes[3], (1, 14), (1, 21), (1, 18))
        self.assertPosition(nodes[4], (1, 23), (1, 30), (1, 27))
        self.assertPosition(nodes[5], (3, 1), (4, 16), (4, 13))
        self.assertPosition(nodes[6], (3, 1), (4, 7), (3, 24))
        self.assertPosition(nodes[7], (3, 1), (3, 8), (3, 5))
        self.assertPosition(nodes[8], (3, 14), (3, 21), (3, 18))

    def test_name(self):
        code = (b"#bla\n"
                b"abc")
        nodes = get_nodes(code, ast.Name)
        self.assertPosition(nodes[0], (2, 0), (2, 3), (2, 3))
