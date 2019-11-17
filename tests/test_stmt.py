# Copyright (c) 2016 Universidade Federal Fluminense (UFF)
# This file is part of PyPosAST.
# Please, consult the license terms in the LICENSE file.

from __future__ import (absolute_import, division)

import ast
import sys

from .utils import get_nodes, NodeTestCase
from .utils import only_python2, only_python3, only_python35, only_python36


def nprint(nodes):
    for i, node in enumerate(nodes):
        print(i, node.lineno, node.col_offset)


class TestStmt(NodeTestCase):
    # pylint: disable=missing-docstring, too-many-public-methods

    def test_pass(self):
        code = ("#bla\n"
                "pass")
        nodes = get_nodes(code, ast.Pass)
        self.assertPosition(nodes[0], (2, 0), (2, 4), (2, 4))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_break(self):
        code = ("#bla\n"
                "break")
        nodes = get_nodes(code, ast.Break)
        self.assertPosition(nodes[0], (2, 0), (2, 5), (2, 5))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_continue(self):
        code = ("#bla\n"
                "continue")
        nodes = get_nodes(code, ast.Continue)
        self.assertPosition(nodes[0], (2, 0), (2, 8), (2, 8))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_expr(self):
        code = ("#bla\n"
                "a")
        nodes = get_nodes(code, ast.Expr)
        self.assertPosition(nodes[0], (2, 0), (2, 1), (2, 1))
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python3
    def test_non_local(self):
        code = ("#bla\n"
                "nonlocal a,\\\n"
                "b")
        nodes = get_nodes(code, ast.Nonlocal)
        self.assertPosition(nodes[0], (2, 0), (3, 1), (2, 8))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 8), (2, 8), 'nonlocal')
        self.assertOperation(nodes[0].op_pos[1], (2, 10), (2, 11), (2, 11), ',')
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_global(self):
        code = ("#bla\n"
                "global a,\\\n"
                "b")
        nodes = get_nodes(code, ast.Global)
        self.assertPosition(nodes[0], (2, 0), (3, 1), (2, 6))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 6), (2, 6), 'global')
        self.assertOperation(nodes[0].op_pos[1], (2, 8), (2, 9), (2, 9), ',')
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python2
    def test_exec(self):
        code = ("#bla\n"
                "exec a in\\\n"
                "b, c")
        nodes = get_nodes(code, ast.Exec)
        self.assertPosition(nodes[0], (2, 0), (3, 4), (2, 4))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 4), (2, 4), 'exec')
        self.assertOperation(nodes[0].op_pos[1], (2, 7), (2, 9), (2, 9), 'in')
        self.assertOperation(nodes[0].op_pos[2], (3, 1), (3, 2), (3, 2), ',')
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python2
    def test_exec2(self):
        code = ("#bla\n"
                "exec a")
        nodes = get_nodes(code, ast.Exec)
        self.assertPosition(nodes[0], (2, 0), (2, 6), (2, 4))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 4), (2, 4), 'exec')
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python2
    def test_exec3(self):
        code = ("#bla\n"
                "exec(a)\n"
                "exec(b)")
        nodes = get_nodes(code, ast.Exec)
        self.assertPosition(nodes[0], (2, 0), (2, 7), (2, 4))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 4), (2, 4), 'exec')
        self.assertNoBeforeInnerAfter(nodes[0])
        self.assertPosition(nodes[1], (3, 0), (3, 7), (3, 4))
        self.assertOperation(nodes[1].op_pos[0], (3, 0), (3, 4), (3, 4), 'exec')
        self.assertNoBeforeInnerAfter(nodes[1])

    def test_import_from(self):
        code = ("#bla\n"
                "from ast import Name,\\\n"
                "Expr as e")
        nodes = get_nodes(code, ast.ImportFrom)
        self.assertPosition(nodes[0], (2, 0), (3, 9), (2, 4))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 4), (2, 4), 'from')
        self.assertOperation(nodes[0].op_pos[1], (2, 9), (2, 15), (2, 15), 'import')
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_import_from2(self):
        code = ("#bla\n"
                "from ast import (Name,\n"
                "Expr as e )")
        nodes = get_nodes(code, ast.ImportFrom)
        self.assertPosition(nodes[0], (2, 0), (3, 11), (2, 4))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 4), (2, 4), 'from')
        self.assertOperation(nodes[0].op_pos[1], (2, 9), (2, 15), (2, 15), 'import')
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_import_from3(self):
        code = ("#bla\n"
                "from . import get_config")
        nodes = get_nodes(code, ast.ImportFrom)
        self.assertPosition(nodes[0], (2, 0), (2, 24), (2, 4))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 4), (2, 4), 'from')
        self.assertOperation(nodes[0].op_pos[1], (2, 7), (2, 13), (2, 13), 'import')
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_import_from4(self):
        code = ("#bla\n"
                "from . import *")
        nodes = get_nodes(code, ast.ImportFrom)
        self.assertPosition(nodes[0], (2, 0), (2, 15), (2, 4))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 4), (2, 4), 'from')
        self.assertOperation(nodes[0].op_pos[1], (2, 7), (2, 13), (2, 13), 'import')
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_import_from5(self):
        code = ("#bla\n"
                "from ast import(Name)\n"
                "from ast import(Expr as e )")
        nodes = get_nodes(code, ast.ImportFrom)
        self.assertPosition(nodes[0], (2, 0), (2, 21), (2, 4))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 4), (2, 4), 'from')
        self.assertOperation(nodes[0].op_pos[1], (2, 9), (2, 15), (2, 15), 'import')
        self.assertNoBeforeInnerAfter(nodes[0])
        self.assertPosition(nodes[1], (3, 0), (3, 27), (3, 4))
        self.assertOperation(nodes[1].op_pos[0], (3, 0), (3, 4), (3, 4), 'from')
        self.assertOperation(nodes[1].op_pos[1], (3, 9), (3, 15), (3, 15), 'import')
        self.assertNoBeforeInnerAfter(nodes[1])

    def test_import(self):
        code = ("#bla\n"
                "import a,\\\n"
                "b as c")
        nodes = get_nodes(code, ast.Import)
        self.assertPosition(nodes[0], (2, 0), (3, 6), (2, 6))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 6), (2, 6), 'import')
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_import2(self):
        code = ("#bla\n"
                "import ab.cd. ef as gh")
        nodes = get_nodes(code, ast.Import)
        self.assertPosition(nodes[0], (2, 0), (2, 22), (2, 6))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 6), (2, 6), 'import')
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_assert(self):
        code = ("#bla\n"
                "assert a,\\\n"
                "b")
        nodes = get_nodes(code, ast.Assert)
        self.assertPosition(nodes[0], (2, 0), (3, 1), (2, 6))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 6), (2, 6), 'assert')
        self.assertOperation(nodes[0].op_pos[1], (2, 8), (2, 9), (2, 9), ',')
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_assert2(self):
        code = ("#bla\n"
                "assert(a)")
        nodes = get_nodes(code, ast.Assert)
        self.assertPosition(nodes[0], (2, 0), (2, 9), (2, 6))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 6), (2, 6), 'assert')
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python2
    def test_try_finally(self):
        code = ("#bla\n"
                "try:\n"
                "    a\n"
                "finally:\n"
                "    b")
        nodes = get_nodes(code, ast.TryFinally)
        self.assertPosition(nodes[0], (2, 0), (5, 5), (2, 3))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 4), (2, 4), 'try:')
        self.assertOperation(nodes[0].op_pos[1], (4, 0), (4, 8), (4, 8), 'finally:')
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python2
    def test_try_except(self):
        code = ("#bla\n"
                "try:\n"
                "    a\n"
                "except (Exception1, Exception2), target:\n"
                "    b")
        nodes = get_nodes(code, ast.TryExcept)
        self.assertPosition(nodes[0], (2, 0), (5, 5), (2, 3))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 4), (2, 4), 'try:')
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python2
    def test_try_except2(self):
        code = ("#bla\n"
                "try:\n"
                "    a\n"
                "except (Exception1, Exception2), target:\n"
                "    b\n"
                "else:\n"
                "    c\n"
                "finally:\n"
                "    d")
        nodes = get_nodes(code, ast.TryExcept)
        self.assertPosition(nodes[0], (2, 0), (7, 5), (2, 3))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 4), (2, 4), 'try:')
        self.assertOperation(nodes[0].op_pos[1], (6, 0), (6, 5), (6, 5), 'else:')
        self.assertNoBeforeInnerAfter(nodes[0])
        nodes = get_nodes(code, ast.TryFinally)
        self.assertPosition(nodes[0], (2, 0), (9, 5), (2, 3))
        self.assertOperation(nodes[0].op_pos[0], (8, 0), (8, 8), (8, 8), 'finally:')

    @only_python3
    def test_try(self):
        code = ("#bla\n"
                "try:\n"
                "    a\n"
                "except (Exception1, Exception2) as target:\n"
                "    b\n"
                "else:\n"
                "    c\n"
                "finally:\n"
                "    d")
        nodes = get_nodes(code, ast.Try)
        self.assertPosition(nodes[0], (2, 0), (9, 5), (2, 3))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 4), (2, 4), 'try:')
        self.assertOperation(nodes[0].op_pos[1], (6, 0), (6, 5), (6, 5), 'else:')
        self.assertOperation(nodes[0].op_pos[2], (8, 0), (8, 8), (8, 8), 'finally:')
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_raise(self):
        code = ("#bla\n"
                "raise E")
        nodes = get_nodes(code, ast.Raise)
        self.assertPosition(nodes[0], (2, 0), (2, 7), (2, 5))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 5), (2, 5), 'raise')
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python2
    def test_raise2(self):
        code = ("#bla\n"
                "raise E, \\\n"
                "V")
        nodes = get_nodes(code, ast.Raise)
        self.assertPosition(nodes[0], (2, 0), (3, 1), (2, 5))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 5), (2, 5), 'raise')
        self.assertOperation(nodes[0].op_pos[1], (2, 7), (2, 8), (2, 8), ',')
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python3
    def test_raise3(self):
        code = ("#bla\n"
                "raise E(\n"
                "V)")
        nodes = get_nodes(code, ast.Raise)
        self.assertPosition(nodes[0], (2, 0), (3, 2), (2, 5))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 5), (2, 5), 'raise')
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python2
    def test_raise4(self):
        code = ("#bla\n"
                "raise(E,\n"
                "V, T)")
        nodes = get_nodes(code, ast.Raise)
        self.assertPosition(nodes[0], (2, 0), (3, 5), (2, 5))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 5), (2, 5), 'raise')
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python2
    def test_raise5(self):
        code = ("#bla\n"
                "raise E,\\\n"
                "V, T")
        nodes = get_nodes(code, ast.Raise)
        self.assertPosition(nodes[0], (2, 0), (3, 4), (2, 5))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 5), (2, 5), 'raise')
        self.assertOperation(nodes[0].op_pos[1], (2, 7), (2, 8), (2, 8), ',')
        self.assertOperation(nodes[0].op_pos[2], (3, 1), (3, 2), (3, 2), ',')
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python3
    def test_raise6(self):
        code = ("#bla\n"
                "raise E(V).with_traceback(T)")
        nodes = get_nodes(code, ast.Raise)
        self.assertPosition(nodes[0], (2, 0), (2, 28), (2, 5))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 5), (2, 5), 'raise')
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python3
    def test_raise7(self):
        code = ("#bla\n"
                "raise E from T")
        nodes = get_nodes(code, ast.Raise)
        self.assertPosition(nodes[0], (2, 0), (2, 14), (2, 5))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 5), (2, 5), 'raise')
        self.assertOperation(nodes[0].op_pos[1], (2, 8), (2, 12), (2, 12), 'from')
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_with(self):
        code = ("#bla\n"
                "with x as f:\n"
                "    a")
        nodes = get_nodes(code, ast.With)
        self.assertPosition(nodes[0], (2, 0), (3, 5), (2, 4))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 4), (2, 4), 'with')
        if sys.version_info < (3, 0):
            self.assertOperation(nodes[0].op_pos[1], (2, 7), (2, 9), (2, 9), 'as')
        self.assertOperation(nodes[0].op_pos[-1], (2, 11), (2, 12), (2, 12), ':')
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_with2(self):
        code = ("#bla\n"
                "with x as f, y as f2:\n"
                "    a")
        nodes = get_nodes(code, ast.With)
        self.assertPosition(nodes[0], (2, 0), (3, 5), (2, 4))
        self.assertNoBeforeInnerAfter(nodes[0])
        if sys.version_info < (3, 0):
            self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 4), (2, 4), 'with')
            self.assertOperation(nodes[0].op_pos[1], (2, 7), (2, 9), (2, 9), 'as')
            self.assertOperation(nodes[1].op_pos[0], (2, 11), (2, 12), (2, 12), ',')
            self.assertOperation(nodes[1].op_pos[1], (2, 15), (2, 17), (2, 17), 'as')
            self.assertOperation(nodes[1].op_pos[2], (2, 20), (2, 21), (2, 21), ':')
            self.assertNoBeforeInnerAfter(nodes[1])
        else:
            self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 4), (2, 4), 'with')
            self.assertOperation(nodes[0].op_pos[1], (2, 11), (2, 12), (2, 12), ',')
            self.assertOperation(nodes[0].op_pos[2], (2, 20), (2, 21), (2, 21), ':')

    @only_python35
    def test_async_with(self):
        code = ("async def f():\n"
                "    async with x as f:\n"
                "        a")
        nodes = get_nodes(code, ast.AsyncWith)
        self.assertPosition(nodes[0], (2, 4), (3, 9), (2, 14))
        self.assertOperation(nodes[0].op_pos[0], (2, 4), (2, 14), (2, 14), 'async with')
        self.assertOperation(nodes[0].op_pos[1], (2, 21), (2, 22), (2, 22), ':')
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_if(self):
        code = ("#bla\n"
                "if x:\n"
                "    a")
        nodes = get_nodes(code, ast.If)
        self.assertPosition(nodes[0], (2, 0), (3, 5), (2, 2))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 2), (2, 2), 'if')
        self.assertOperation(nodes[0].op_pos[1], (2, 4), (2, 5), (2, 5), ':')
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_if2(self):
        code = ("#bla\n"
                "if x:\n"
                "    a\n"
                "elif y:\n"
                "    b")
        nodes = get_nodes(code, ast.If)
        self.assertPosition(nodes[0], (2, 0), (5, 5), (2, 2))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 2), (2, 2), 'if')
        self.assertOperation(nodes[0].op_pos[1], (2, 4), (2, 5), (2, 5), ':')
        self.assertNoBeforeInnerAfter(nodes[0])
        self.assertPosition(nodes[1], (4, 0), (5, 5), (4, 4))
        self.assertOperation(nodes[1].op_pos[0], (4, 0), (4, 4), (4, 4), 'elif')
        self.assertOperation(nodes[1].op_pos[1], (4, 6), (4, 7), (4, 7), ':')
        self.assertNoBeforeInnerAfter(nodes[1])

    def test_if3(self):
        code = ("#bla\n"
                "if x:\n"
                "    a\n"
                "elif y:\n"
                "    b\n"
                "if z:\n"
                "    c")
        nodes = get_nodes(code, ast.If)
        self.assertPosition(nodes[0], (2, 0), (5, 5), (2, 2))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 2), (2, 2), 'if')
        self.assertOperation(nodes[0].op_pos[1], (2, 4), (2, 5), (2, 5), ':')
        self.assertNoBeforeInnerAfter(nodes[0])
        self.assertPosition(nodes[1], (4, 0), (5, 5), (4, 4))
        self.assertOperation(nodes[1].op_pos[0], (4, 0), (4, 4), (4, 4), 'elif')
        self.assertOperation(nodes[1].op_pos[1], (4, 6), (4, 7), (4, 7), ':')
        self.assertNoBeforeInnerAfter(nodes[1])
        self.assertPosition(nodes[2], (6, 0), (7, 5), (6, 2))
        self.assertOperation(nodes[2].op_pos[0], (6, 0), (6, 2), (6, 2), 'if')
        self.assertOperation(nodes[2].op_pos[1], (6, 4), (6, 5), (6, 5), ':')
        self.assertNoBeforeInnerAfter(nodes[2])

    def test_if4(self):
        code = ("#bla\n"
                "if x:\n"
                "    a\n"
                "elif y:\n"
                "    b\n"
                "else:\n"
                "    c")
        nodes = get_nodes(code, ast.If)
        self.assertPosition(nodes[0], (2, 0), (7, 5), (2, 2))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 2), (2, 2), 'if')
        self.assertOperation(nodes[0].op_pos[1], (2, 4), (2, 5), (2, 5), ':')
        self.assertNoBeforeInnerAfter(nodes[0])
        self.assertPosition(nodes[1], (4, 0), (7, 5), (4, 4))
        self.assertOperation(nodes[1].op_pos[0], (4, 0), (4, 4), (4, 4), 'elif')
        self.assertOperation(nodes[1].op_pos[1], (4, 6), (4, 7), (4, 7), ':')
        self.assertOperation(nodes[1].op_pos[2], (6, 0), (6, 5), (6, 5), 'else:')
        self.assertNoBeforeInnerAfter(nodes[1])

    def test_if5(self):
        # Bug report by Vitor
        code = ("#bla\n"
                "if(x):\n"
                "    a\n"
                "elif(y):\n"
                "    b\n"
                "else:\n"
                "    c")
        nodes = get_nodes(code, ast.If)
        self.assertPosition(nodes[0], (2, 0), (7, 5), (2, 2))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 2), (2, 2), 'if')
        self.assertOperation(nodes[0].op_pos[1], (2, 5), (2, 6), (2, 6), ':')
        self.assertNoBeforeInnerAfter(nodes[0])
        self.assertPosition(nodes[1], (4, 0), (7, 5), (4, 4))
        self.assertOperation(nodes[1].op_pos[0], (4, 0), (4, 4), (4, 4), 'elif')
        self.assertOperation(nodes[1].op_pos[1], (4, 7), (4, 8), (4, 8), ':')
        self.assertOperation(nodes[1].op_pos[2], (6, 0), (6, 5), (6, 5), 'else:')
        self.assertNoBeforeInnerAfter(nodes[1])

    def test_while(self):
        code = ("#bla\n"
                "while x:\n"
                "    a")
        nodes = get_nodes(code, ast.While)
        self.assertPosition(nodes[0], (2, 0), (3, 5), (2, 5))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 5), (2, 5), 'while')
        self.assertOperation(nodes[0].op_pos[1], (2, 7), (2, 8), (2, 8), ':')
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_while2(self):
        code = ("#bla\n"
                "while x:\n"
                "    a\n"
                "else:\n"
                "    b")
        nodes = get_nodes(code, ast.While)
        self.assertPosition(nodes[0], (2, 0), (5, 5), (2, 5))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 5), (2, 5), 'while')
        self.assertOperation(nodes[0].op_pos[1], (2, 7), (2, 8), (2, 8), ':')
        self.assertOperation(nodes[0].op_pos[2], (4, 0), (4, 5), (4, 5), 'else:')
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_while3(self):
        code = ("#bla\n"
                "while(x):\n"
                "    while(y):\n"
                "        a")
        nodes = get_nodes(code, ast.While)
        self.assertPosition(nodes[0], (2, 0), (4, 9), (2, 5))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 5), (2, 5), 'while')
        self.assertOperation(nodes[0].op_pos[1], (2, 8), (2, 9), (2, 9), ':')
        self.assertNoBeforeInnerAfter(nodes[0])
        self.assertPosition(nodes[1], (3, 4), (4, 9), (3, 9))
        self.assertOperation(nodes[1].op_pos[0], (3, 4), (3, 9), (3, 9), 'while')
        self.assertOperation(nodes[1].op_pos[1], (3, 12), (3, 13), (3, 13), ':')
        self.assertNoBeforeInnerAfter(nodes[1])

    def test_for(self):
        code = ("#bla\n"
                "for x in l:\n"
                "    a")
        nodes = get_nodes(code, ast.For)
        self.assertPosition(nodes[0], (2, 0), (3, 5), (2, 3))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 3), (2, 3), 'for')
        self.assertOperation(nodes[0].op_pos[1], (2, 6), (2, 8), (2, 8), 'in')
        self.assertOperation(nodes[0].op_pos[2], (2, 10), (2, 11), (2, 11), ':')
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_for2(self):
        code = ("#bla\n"
                "for x in l:\n"
                "    a\n"
                "else:\n"
                "    b")
        nodes = get_nodes(code, ast.For)
        self.assertPosition(nodes[0], (2, 0), (5, 5), (2, 3))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 3), (2, 3), 'for')
        self.assertOperation(nodes[0].op_pos[1], (2, 6), (2, 8), (2, 8), 'in')
        self.assertOperation(nodes[0].op_pos[2], (2, 10), (2, 11), (2, 11), ':')
        self.assertOperation(nodes[0].op_pos[3], (4, 0), (4, 5), (4, 5), 'else:')
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_for3(self):
        code = ("#bla\n"
                "for(x)in(l):\n"
                "    a\n"
                "for(y)in(m):\n"
                "    n\n")
        nodes = get_nodes(code, ast.For)
        self.assertPosition(nodes[0], (2, 0), (3, 5), (2, 3))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 3), (2, 3), 'for')
        self.assertOperation(nodes[0].op_pos[1], (2, 6), (2, 8), (2, 8), 'in')
        self.assertOperation(nodes[0].op_pos[2], (2, 11), (2, 12), (2, 12), ':')
        self.assertNoBeforeInnerAfter(nodes[0])
        self.assertPosition(nodes[1], (4, 0), (5, 5), (4, 3))
        self.assertOperation(nodes[1].op_pos[0], (4, 0), (4, 3), (4, 3), 'for')
        self.assertOperation(nodes[1].op_pos[1], (4, 6), (4, 8), (4, 8), 'in')
        self.assertOperation(nodes[1].op_pos[2], (4, 11), (4, 12), (4, 12), ':')
        self.assertNoBeforeInnerAfter(nodes[1])

    @only_python35
    def test_async_for(self):
        code = ("async def f():\n"
                "    async for x in l:\n"
                "        a")
        nodes = get_nodes(code, ast.AsyncFor)
        self.assertPosition(nodes[0], (2, 4), (3, 9), (2, 13))
        self.assertOperation(nodes[0].op_pos[0], (2, 4), (2, 13), (2, 13), 'async for')
        self.assertOperation(nodes[0].op_pos[1], (2, 16), (2, 18), (2, 18), 'in')
        self.assertOperation(nodes[0].op_pos[2], (2, 20), (2, 21), (2, 21), ':')
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python35
    def test_async_for2(self):
        code = ("async def f():\n"
                "    async for(x)in(l):\n"
                "        a\n"
                "    async for(y)in(m):\n"
                "        b")
        nodes = get_nodes(code, ast.AsyncFor)
        self.assertPosition(nodes[0], (2, 4), (3, 9), (2, 13))
        self.assertOperation(nodes[0].op_pos[0], (2, 4), (2, 13), (2, 13), 'async for')
        self.assertOperation(nodes[0].op_pos[1], (2, 16), (2, 18), (2, 18), 'in')
        self.assertOperation(nodes[0].op_pos[2], (2, 21), (2, 22), (2, 22), ':')
        self.assertNoBeforeInnerAfter(nodes[0])
        self.assertPosition(nodes[1], (4, 4), (5, 9), (4, 13))
        self.assertOperation(nodes[1].op_pos[0], (4, 4), (4, 13), (4, 13), 'async for')
        self.assertOperation(nodes[1].op_pos[1], (4, 16), (4, 18), (4, 18), 'in')
        self.assertOperation(nodes[1].op_pos[2], (4, 21), (4, 22), (4, 22), ':')
        self.assertNoBeforeInnerAfter(nodes[1])

    @only_python2
    def test_print(self):
        code = ("#bla\n"
                "print")
        nodes = get_nodes(code, ast.Print)
        self.assertPosition(nodes[0], (2, 0), (2, 5), (2, 5))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 5), (2, 5), 'print')
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python2
    def test_print2(self):
        code = ("#bla\n"
                "print a")
        nodes = get_nodes(code, ast.Print)
        self.assertPosition(nodes[0], (2, 0), (2, 7), (2, 5))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 5), (2, 5), 'print')
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python2
    def test_print3(self):
        code = ("#bla\n"
                "print >>log, a")
        nodes = get_nodes(code, ast.Print)
        self.assertPosition(nodes[0], (2, 0), (2, 14), (2, 5))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 5), (2, 5), 'print')
        self.assertOperation(nodes[0].op_pos[1], (2, 6), (2, 8), (2, 8), '>>')
        self.assertOperation(nodes[0].op_pos[2], (2, 11), (2, 12), (2, 12), ',')
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python2
    def test_print4(self):
        code = ("#bla\n"
                "print >>log")
        nodes = get_nodes(code, ast.Print)
        self.assertPosition(nodes[0], (2, 0), (2, 11), (2, 5))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 5), (2, 5), 'print')
        self.assertOperation(nodes[0].op_pos[1], (2, 6), (2, 8), (2, 8), '>>')
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python2
    def test_print5(self):
        code = ("#bla\n"
                "print(a)\n"
                "print(b)")
        nodes = get_nodes(code, ast.Print)
        self.assertPosition(nodes[0], (2, 0), (2, 8), (2, 5))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 5), (2, 5), 'print')
        self.assertNoBeforeInnerAfter(nodes[0])
        self.assertPosition(nodes[1], (3, 0), (3, 8), (3, 5))
        self.assertOperation(nodes[1].op_pos[0], (3, 0), (3, 5), (3, 5), 'print')
        self.assertNoBeforeInnerAfter(nodes[1])

    def test_aug_assign(self):
        code = ("#bla\n"
                "a += 1")
        nodes = get_nodes(code, ast.AugAssign)
        self.assertPosition(nodes[0], (2, 0), (2, 6), (2, 4))
        self.assertOperation(nodes[0].op_pos[0], (2, 2), (2, 4), (2, 4), '+=')
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python36
    def test_ann_assign(self):
        code = ("#bla\n"
                "a: int = 1")
        nodes = get_nodes(code, ast.AnnAssign)
        self.assertPosition(nodes[0], (2, 0), (2, 10), (2, 2))
        self.assertOperation(nodes[0].op_pos[0], (2, 1), (2, 2), (2, 2), ':')
        self.assertOperation(nodes[0].op_pos[1], (2, 7), (2, 8), (2, 8), '=')
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python36
    def test_ann_assign2(self):
        code = ("#bla\n"
                "a: int")
        nodes = get_nodes(code, ast.AnnAssign)
        self.assertPosition(nodes[0], (2, 0), (2, 6), (2, 2))
        self.assertOperation(nodes[0].op_pos[0], (2, 1), (2, 2), (2, 2), ':')
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python36
    def test_ann_assign3(self):
        code = ("#bla\n"
                "(a): int")
        nodes = get_nodes(code, ast.AnnAssign)
        self.assertPosition(nodes[0], (2, 0), (2, 8), (2, 4))
        self.assertOperation(nodes[0].op_pos[0], (2, 3), (2, 4), (2, 4), ':')
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python36
    def test_ann_assign4(self):
        code = ("#bla\n"
                "(a):(int)\n"
                "(b):(str)")
        nodes = get_nodes(code, ast.AnnAssign)
        self.assertPosition(nodes[0], (2, 0), (2, 9), (2, 4))
        self.assertOperation(nodes[0].op_pos[0], (2, 3), (2, 4), (2, 4), ':')
        self.assertNoBeforeInnerAfter(nodes[0])
        self.assertPosition(nodes[1], (3, 0), (3, 9), (3, 4))
        self.assertOperation(nodes[1].op_pos[0], (3, 3), (3, 4), (3, 4), ':')
        self.assertNoBeforeInnerAfter(nodes[1])

    def test_assign(self):
        code = ("#bla\n"
                "a = b = c =\\\n"
                "4")
        nodes = get_nodes(code, ast.Assign)
        self.assertPosition(nodes[0], (2, 0), (3, 1), (3, 1))
        self.assertOperation(nodes[0].op_pos[0], (2, 2), (2, 3), (2, 3), '=')
        self.assertOperation(nodes[0].op_pos[1], (2, 6), (2, 7), (2, 7), '=')
        self.assertOperation(nodes[0].op_pos[2], (2, 10), (2, 11), (2, 11), '=')
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_assign2(self):
        code = ("#bla\n"
                "(a)=(b)\n"
                "(c)=(d)")
        nodes = get_nodes(code, ast.Assign)
        self.assertPosition(nodes[0], (2, 0), (2, 7), (2, 7))
        self.assertOperation(nodes[0].op_pos[0], (2, 3), (2, 4), (2, 4), '=')
        self.assertNoBeforeInnerAfter(nodes[0])
        self.assertPosition(nodes[1], (3, 0), (3, 7), (3, 7))
        self.assertOperation(nodes[1].op_pos[0], (3, 3), (3, 4), (3, 4), '=')
        self.assertNoBeforeInnerAfter(nodes[1])

    def test_delete(self):
        code = ("#bla\n"
                "del a, b")
        nodes = get_nodes(code, ast.Delete)
        self.assertPosition(nodes[0], (2, 0), (2, 8), (2, 3))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 3), (2, 3), 'del')
        self.assertOperation(nodes[0].op_pos[1], (2, 5), (2, 6), (2, 6), ',')
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_delete2(self):
        code = ("#bla\n"
                "del(a, \n"
                "b)")
        nodes = get_nodes(code, ast.Delete)
        self.assertPosition(nodes[0], (2, 0), (3, 2), (2, 3))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 3), (2, 3), 'del')
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_delete3(self):
        code = ("#bla\n"
                "del(a, b)\n"
                "del(c, d)")
        nodes = get_nodes(code, ast.Delete)
        self.assertPosition(nodes[0], (2, 0), (2, 9), (2, 3))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 3), (2, 3), 'del')
        self.assertNoBeforeInnerAfter(nodes[0])
        self.assertPosition(nodes[1], (3, 0), (3, 9), (3, 3))
        self.assertOperation(nodes[1].op_pos[0], (3, 0), (3, 3), (3, 3), 'del')
        self.assertNoBeforeInnerAfter(nodes[1])

    def test_return(self):
        code = ("#bla\n"
                "return")
        nodes = get_nodes(code, ast.Return)
        self.assertPosition(nodes[0], (2, 0), (2, 6), (2, 6))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 6), (2, 6), 'return')
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_return2(self):
        code = ("#bla\n"
                "return a")
        nodes = get_nodes(code, ast.Return)
        self.assertPosition(nodes[0], (2, 0), (2, 8), (2, 6))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 6), (2, 6), 'return')
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_return3(self):
        code = ("#bla\n"
                "return(a)\n"
                "return(b)")
        nodes = get_nodes(code, ast.Return)
        self.assertPosition(nodes[0], (2, 0), (2, 9), (2, 6))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 6), (2, 6), 'return')
        self.assertNoBeforeInnerAfter(nodes[0])
        self.assertPosition(nodes[1], (3, 0), (3, 9), (3, 6))
        self.assertOperation(nodes[1].op_pos[0], (3, 0), (3, 6), (3, 6), 'return')
        self.assertNoBeforeInnerAfter(nodes[1])

    def test_class(self):
        code = ("#bla\n"
                "class a:\n"
                "    pass")
        nodes = get_nodes(code, ast.ClassDef)
        self.assertPosition(nodes[0], (2, 0), (3, 8), (2, 5))
        self.assertPosition(nodes[0].name_node, (2, 6), (2, 7), (2, 7))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 5), (2, 5), 'class')
        self.assertOperation(nodes[0].op_pos[1], (2, 7), (2, 8), (2, 8), ':')
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_class2(self):
        code = ("#bla\n"
                "@dec1\n"
                "class a(object):\n"
                "    pass")
        nodes = get_nodes(code, ast.ClassDef)
        self.assertPosition(nodes[0], (2, 0), (4, 8), (3, 5))
        self.assertPosition(nodes[0].name_node, (3, 6), (3, 7), (3, 7))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 1), (2, 1), '@')
        self.assertOperation(nodes[0].op_pos[1], (3, 0), (3, 5), (3, 5), 'class')
        self.assertOperation(nodes[0].op_pos[2], (3, 15), (3, 16), (3, 16), ':')
        self.assertNoBeforeInnerAfter(nodes[0])

        nodes = get_nodes(code, ast.Name)
        self.assertPosition(nodes[0], (3, 8), (3, 14), (3, 14))
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_function_def(self):
        code = ("#bla\n"
                "def f(x, y=2, *z, **w):\n"
                "    pass")
        nodes = get_nodes(code, ast.FunctionDef)

        self.assertPosition(nodes[0], (2, 0), (3, 8), (2, 3))
        self.assertPosition(nodes[0].name_node, (2, 4), (2, 5), (2, 5))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 3), (2, 3), 'def')
        self.assertOperation(nodes[0].op_pos[1], (2, 5), (2, 6), (2, 6), '(')
        self.assertOperation(nodes[0].op_pos[2], (2, 21), (2, 22), (2, 22), ')')
        self.assertOperation(nodes[0].op_pos[3], (2, 22), (2, 23), (2, 23), ':')
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_function_def2(self):
        code = ("#bla\n"
                "@dec1\n"
                "def f(x, y=2, *z, **w):\n"
                "    pass")
        nodes = get_nodes(code, ast.FunctionDef)
        self.assertPosition(nodes[0], (2, 0), (4, 8), (3, 3))
        self.assertPosition(nodes[0].name_node, (3, 4), (3, 5), (3, 5))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 1), (2, 1), '@')
        self.assertOperation(nodes[0].op_pos[1], (3, 0), (3, 3), (3, 3), 'def')
        self.assertOperation(nodes[0].op_pos[2], (3, 5), (3, 6), (3, 6), '(')
        self.assertOperation(nodes[0].op_pos[3], (3, 21), (3, 22), (3, 22), ')')
        self.assertOperation(nodes[0].op_pos[4], (3, 22), (3, 23), (3, 23), ':')
        self.assertNoBeforeInnerAfter(nodes[0])

    @only_python3
    def test_function_def3(self):
        code = ("#bla\n"
                "@dec1\n"
                "def f(x, y=2, *z, **w) -> 'teste':\n"
                "    pass")
        nodes = get_nodes(code, ast.FunctionDef)
        self.assertPosition(nodes[0], (2, 0), (4, 8), (3, 3))
        self.assertPosition(nodes[0].name_node, (3, 4), (3, 5), (3, 5))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 1), (2, 1), '@')
        self.assertOperation(nodes[0].op_pos[1], (3, 0), (3, 3), (3, 3), 'def')
        self.assertOperation(nodes[0].op_pos[2], (3, 5), (3, 6), (3, 6), '(')
        self.assertOperation(nodes[0].op_pos[3], (3, 21), (3, 22), (3, 22), ')')
        self.assertOperation(nodes[0].op_pos[4], (3, 23), (3, 25), (3, 25), '->')
        self.assertOperation(nodes[0].op_pos[5], (3, 33), (3, 34), (3, 34), ':')
        self.assertNoBeforeInnerAfter(nodes[0])

    def test_function_def4(self):
        code = ("#bla\n"
                "def g(x):\n"
                "    return x\n"
                "@g\n"
                "def f():\n"
                "    pass")
        nodes = get_nodes(code, ast.FunctionDef)
        self.assertPosition(nodes[0], (2, 0), (3, 12), (2, 3))
        self.assertPosition(nodes[0].name_node, (2, 4), (2, 5), (2, 5))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 3), (2, 3), 'def')
        self.assertOperation(nodes[0].op_pos[1], (2, 5), (2, 6), (2, 6), '(')
        self.assertOperation(nodes[0].op_pos[2], (2, 7), (2, 8), (2, 8), ')')
        self.assertOperation(nodes[0].op_pos[3], (2, 8), (2, 9), (2, 9), ':')
        self.assertNoBeforeInnerAfter(nodes[0])
        self.assertPosition(nodes[1], (4, 0), (6, 8), (5, 3))
        self.assertPosition(nodes[1].name_node, (5, 4), (5, 5), (5, 5))
        self.assertOperation(nodes[1].op_pos[0], (4, 0), (4, 1), (4, 1), '@')
        self.assertOperation(nodes[1].op_pos[1], (5, 0), (5, 3), (5, 3), 'def')
        self.assertOperation(nodes[1].op_pos[2], (5, 5), (5, 6), (5, 6), '(')
        self.assertOperation(nodes[1].op_pos[3], (5, 6), (5, 7), (5, 7), ')')
        self.assertOperation(nodes[1].op_pos[4], (5, 7), (5, 8), (5, 8), ':')
        self.assertNoBeforeInnerAfter(nodes[1])

    @only_python35
    def test_async_function_def(self):
        code = ("#bla\n"
                "async def f(x, y=2, *z, **w):\n"
                "    pass")
        nodes = get_nodes(code, ast.AsyncFunctionDef)
        self.assertPosition(nodes[0], (2, 0), (3, 8), (2, 9))
        self.assertPosition(nodes[0].name_node, (2, 10), (2, 11), (2, 11))
        self.assertOperation(nodes[0].op_pos[0], (2, 0), (2, 9), (2, 9), 'async def')
        self.assertOperation(nodes[0].op_pos[1], (2, 11), (2, 12), (2, 12), '(')
        self.assertOperation(nodes[0].op_pos[2], (2, 27), (2, 28), (2, 28), ')')
        self.assertOperation(nodes[0].op_pos[3], (2, 28), (2, 29), (2, 29), ':')
        self.assertNoBeforeInnerAfter(nodes[0])
