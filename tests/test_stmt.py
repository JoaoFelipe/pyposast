# Copyright (c) 2016 Universidade Federal Fluminense (UFF)
# This file is part of PyPosAST.
# Please, consult the license terms in the LICENSE file.

from __future__ import (absolute_import, division)

import ast

from .utils import get_nodes, NodeTestCase
from .utils import only_python2, only_python3, only_python35, only_python36


def nprint(nodes):
    for i, node in enumerate(nodes):
        print(i, node.lineno, node.col_offset)


class TestStmt(NodeTestCase):

    def test_pass(self):
        code = ("#bla\n"
                "pass")
        nodes = get_nodes(code, ast.Pass)
        self.assertPosition(nodes[0], (2, 0), (2, 4), (2, 4))

    def test_break(self):
        code = ("#bla\n"
                "break")
        nodes = get_nodes(code, ast.Break)
        self.assertPosition(nodes[0], (2, 0), (2, 5), (2, 5))

    def test_continue(self):
        code = ("#bla\n"
                "continue")
        nodes = get_nodes(code, ast.Continue)
        self.assertPosition(nodes[0], (2, 0), (2, 8), (2, 8))

    def test_expr(self):
        code = ("#bla\n"
                "a")
        nodes = get_nodes(code, ast.Expr)
        self.assertPosition(nodes[0], (2, 0), (2, 1), (2, 1))

    @only_python3
    def test_non_local(self):
        code = ("#bla\n"
                "nonlocal a,\\\n"
                "b")
        nodes = get_nodes(code, ast.Nonlocal)
        self.assertPosition(nodes[0], (2, 0), (3, 1), (2, 8))

    def test_global(self):
        code = ("#bla\n"
                "global a,\\\n"
                "b")
        nodes = get_nodes(code, ast.Global)
        self.assertPosition(nodes[0], (2, 0), (3, 1), (2, 6))

    @only_python2
    def test_exec(self):
        code = ("#bla\n"
                "exec a in\\\n"
                "b, c")
        nodes = get_nodes(code, ast.Exec)
        self.assertPosition(nodes[0], (2, 0), (3, 4), (2, 4))

    @only_python2
    def test_exec2(self):
        code = ("#bla\n"
                "exec a")
        nodes = get_nodes(code, ast.Exec)
        self.assertPosition(nodes[0], (2, 0), (2, 6), (2, 4))

    def test_import_from(self):
        code = ("#bla\n"
                "from ast import Name,\\\n"
                "Expr as e")
        nodes = get_nodes(code, ast.ImportFrom)
        self.assertPosition(nodes[0], (2, 0), (3, 9), (2, 4))

    def test_import_from2(self):
        code = ("#bla\n"
                "from ast import (Name,\n"
                "Expr as e )")
        nodes = get_nodes(code, ast.ImportFrom)
        self.assertPosition(nodes[0], (2, 0), (3, 11), (2, 4))

    def test_import_from3(self):
        code = ("#bla\n"
                "from . import get_config")
        nodes = get_nodes(code, ast.ImportFrom)
        self.assertPosition(nodes[0], (2, 0), (2, 24), (2, 4))

    def test_import_from4(self):
        code = ("#bla\n"
                "from . import *")
        nodes = get_nodes(code, ast.ImportFrom)
        self.assertPosition(nodes[0], (2, 0), (2, 15), (2, 4))

    def test_import(self):
        code = ("#bla\n"
                "import a,\\\n"
                "b as c")
        nodes = get_nodes(code, ast.Import)
        self.assertPosition(nodes[0], (2, 0), (3, 6), (2, 6))

    def test_import2(self):
        code = ("#bla\n"
                "import ab.cd. ef as gh")
        nodes = get_nodes(code, ast.Import)
        self.assertPosition(nodes[0], (2, 0), (2, 22), (2, 6))

    def test_assert(self):
        code = ("#bla\n"
                "assert a,\\\n"
                "b")
        nodes = get_nodes(code, ast.Assert)
        self.assertPosition(nodes[0], (2, 0), (3, 1), (2, 6))

    def test_assert2(self):
        code = ("#bla\n"
                "assert(a)")
        nodes = get_nodes(code, ast.Assert)
        self.assertPosition(nodes[0], (2, 0), (2, 9), (2, 6))

    @only_python2
    def test_try_finally(self):
        code = ("#bla\n"
                "try:\n"
                "    a\n"
                "finally:\n"
                "    b")
        nodes = get_nodes(code, ast.TryFinally)
        self.assertPosition(nodes[0], (2, 0), (5, 5), (2, 3))

    @only_python2
    def test_try_except(self):
        code = ("#bla\n"
                "try:\n"
                "    a\n"
                "except (Exception1, Exception2), target:\n"
                "    b")
        nodes = get_nodes(code, ast.TryExcept)
        self.assertPosition(nodes[0], (2, 0), (5, 5), (2, 3))

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
        nodes = get_nodes(code, ast.TryFinally)
        self.assertPosition(nodes[0], (2, 0), (9, 5), (2, 3))

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

    def test_raise(self):
        code = ("#bla\n"
                "raise E")
        nodes = get_nodes(code, ast.Raise)
        self.assertPosition(nodes[0], (2, 0), (2, 7), (2, 5))

    @only_python2
    def test_raise2(self):
        code = ("#bla\n"
                "raise E, \\\n"
                "V")
        nodes = get_nodes(code, ast.Raise)
        self.assertPosition(nodes[0], (2, 0), (3, 1), (2, 5))

    @only_python3
    def test_raise3(self):
        code = ("#bla\n"
                "raise E(\n"
                "V)")
        nodes = get_nodes(code, ast.Raise)
        self.assertPosition(nodes[0], (2, 0), (3, 2), (2, 5))

    @only_python2
    def test_raise4(self):
        code = ("#bla\n"
                "raise(E,\n"
                "V, T)")
        nodes = get_nodes(code, ast.Raise)
        self.assertPosition(nodes[0], (2, 0), (3, 5), (2, 5))

    @only_python2
    def test_raise5(self):
        code = ("#bla\n"
                "raise E,\\\n"
                "V, T")
        nodes = get_nodes(code, ast.Raise)
        self.assertPosition(nodes[0], (2, 0), (3, 4), (2, 5))

    @only_python3
    def test_raise6(self):
        code = ("#bla\n"
                "raise E(V).with_traceback(T)")
        nodes = get_nodes(code, ast.Raise)
        self.assertPosition(nodes[0], (2, 0), (2, 28), (2, 5))

    def test_with(self):
        code = ("#bla\n"
                "with x as f:\n"
                "    a")
        nodes = get_nodes(code, ast.With)
        self.assertPosition(nodes[0], (2, 0), (3, 5), (2, 4))

    def test_with2(self):
        code = ("#bla\n"
                "with x as f, y as f2:\n"
                "    a")
        nodes = get_nodes(code, ast.With)
        self.assertPosition(nodes[0], (2, 0), (3, 5), (2, 4))

    @only_python35
    def test_async_with(self):
        code = ("async def f():\n"
                "    async with x as f:\n"
                "        a")
        nodes = get_nodes(code, ast.AsyncWith)
        self.assertPosition(nodes[0], (2, 4), (3, 9), (2, 9))

    def test_if(self):
        code = ("#bla\n"
                "if x:\n"
                "    a")
        nodes = get_nodes(code, ast.If)
        self.assertPosition(nodes[0], (2, 0), (3, 5), (2, 2))

    def test_if2(self):
        code = ("#bla\n"
                "if x:\n"
                "    a\n"
                "elif y:\n"
                "    b")
        nodes = get_nodes(code, ast.If)
        self.assertPosition(nodes[0], (2, 0), (5, 5), (2, 2))
        self.assertPosition(nodes[1], (4, 0), (5, 5), (4, 4))

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
        self.assertPosition(nodes[1], (4, 0), (5, 5), (4, 4))
        self.assertPosition(nodes[2], (6, 0), (7, 5), (6, 2))

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
        self.assertPosition(nodes[1], (4, 0), (7, 5), (4, 4))

    def test_while(self):
        code = ("#bla\n"
                "while x:\n"
                "    a")
        nodes = get_nodes(code, ast.While)
        self.assertPosition(nodes[0], (2, 0), (3, 5), (2, 5))

    def test_while2(self):
        code = ("#bla\n"
                "while x:\n"
                "    a\n"
                "else:\n"
                "    b")
        nodes = get_nodes(code, ast.While)
        self.assertPosition(nodes[0], (2, 0), (5, 5), (2, 5))

    def test_for(self):
        code = ("#bla\n"
                "for x in l:\n"
                "    a")
        nodes = get_nodes(code, ast.For)
        self.assertPosition(nodes[0], (2, 0), (3, 5), (2, 3))

    def test_for2(self):
        code = ("#bla\n"
                "for x in l:\n"
                "    a\n"
                "else:\n"
                "    b")
        nodes = get_nodes(code, ast.For)
        self.assertPosition(nodes[0], (2, 0), (5, 5), (2, 3))

    @only_python35
    def test_async_for(self):
        code = ("async def f():\n"
                "    async for x in l:\n"
                "        a")
        nodes = get_nodes(code, ast.AsyncFor)
        self.assertPosition(nodes[0], (2, 4), (3, 9), (2, 9))

    @only_python2
    def test_print(self):
        code = ("#bla\n"
                "print")
        nodes = get_nodes(code, ast.Print)
        self.assertPosition(nodes[0], (2, 0), (2, 5), (2, 5))

    @only_python2
    def test_print2(self):
        code = ("#bla\n"
                "print a")
        nodes = get_nodes(code, ast.Print)
        self.assertPosition(nodes[0], (2, 0), (2, 7), (2, 5))

    @only_python2
    def test_print3(self):
        code = ("#bla\n"
                "print >>log, a")
        nodes = get_nodes(code, ast.Print)
        self.assertPosition(nodes[0], (2, 0), (2, 14), (2, 5))

    @only_python2
    def test_print4(self):
        code = ("#bla\n"
                "print >>log")
        nodes = get_nodes(code, ast.Print)
        self.assertPosition(nodes[0], (2, 0), (2, 11), (2, 5))

    def test_aug_assign(self):
        code = ("#bla\n"
                "a += 1")
        nodes = get_nodes(code, ast.AugAssign)
        self.assertPosition(nodes[0], (2, 0), (2, 6), (2, 4))
        self.assertPosition(nodes[0].op_pos, (2, 2), (2, 4), (2, 4))

    @only_python36
    def test_ann_assign(self):
        code = ("#bla\n"
                "a: int = 1")
        nodes = get_nodes(code, ast.AnnAssign)
        self.assertPosition(nodes[0], (2, 0), (2, 10), (2, 2))
        self.assertPosition(nodes[0].op_pos[0], (2, 1), (2, 2), (2, 2))
        self.assertPosition(nodes[0].op_pos[1], (2, 7), (2, 8), (2, 8))

    @only_python36
    def test_ann_assign2(self):
        code = ("#bla\n"
                "a: int")
        nodes = get_nodes(code, ast.AnnAssign)
        self.assertPosition(nodes[0], (2, 0), (2, 6), (2, 2))
        self.assertPosition(nodes[0].op_pos[0], (2, 1), (2, 2), (2, 2))

    @only_python36
    def test_ann_assign3(self):
        code = ("#bla\n"
                "(a): int")
        nodes = get_nodes(code, ast.AnnAssign)
        self.assertPosition(nodes[0], (2, 0), (2, 8), (2, 4))
        self.assertPosition(nodes[0].op_pos[0], (2, 3), (2, 4), (2, 4))

    def test_assign(self):
        code = ("#bla\n"
                "a = b = c =\\\n"
                "4")
        nodes = get_nodes(code, ast.Assign)
        self.assertPosition(nodes[0], (2, 0), (3, 1), (3, 1))
        self.assertPosition(nodes[0].op_pos[0], (2, 2), (2, 3), (2, 3))
        self.assertPosition(nodes[0].op_pos[1], (2, 6), (2, 7), (2, 7))
        self.assertPosition(nodes[0].op_pos[2], (2, 10), (2, 11), (2, 11))

    def test_delete(self):
        code = ("#bla\n"
                "del a, b")
        nodes = get_nodes(code, ast.Delete)
        self.assertPosition(nodes[0], (2, 0), (2, 8), (2, 3))

    def test_delete2(self):
        code = ("#bla\n"
                "del(a, \n"
                "b)")
        nodes = get_nodes(code, ast.Delete)
        self.assertPosition(nodes[0], (2, 0), (3, 2), (2, 3))

    def test_return(self):
        code = ("#bla\n"
                "return")
        nodes = get_nodes(code, ast.Return)
        self.assertPosition(nodes[0], (2, 0), (2, 6), (2, 6))

    def test_return2(self):
        code = ("#bla\n"
                "return a")
        nodes = get_nodes(code, ast.Return)
        self.assertPosition(nodes[0], (2, 0), (2, 8), (2, 6))

    def test_class(self):
        code = ("#bla\n"
                "class a:\n"
                "    pass")
        nodes = get_nodes(code, ast.ClassDef)
        self.assertPosition(nodes[0], (2, 0), (3, 8), (2, 5))

    def test_class2(self):
        code = ("#bla\n"
                "@dec1\n"
                "class a(object):\n"
                "    pass")
        nodes = get_nodes(code, ast.ClassDef)
        self.assertPosition(nodes[0], (2, 0), (4, 8), (3, 5))

    def test_function_def(self):
        code = ("#bla\n"
                "def f(x, y=2, *z, **w):\n"
                "    pass")
        nodes = get_nodes(code, ast.FunctionDef)
        self.assertPosition(nodes[0], (2, 0), (3, 8), (2, 3))

    def test_function_def2(self):
        code = ("#bla\n"
                "@dec1\n"
                "def f(x, y=2, *z, **w):\n"
                "    pass")
        nodes = get_nodes(code, ast.FunctionDef)
        self.assertPosition(nodes[0], (2, 0), (4, 8), (3, 3))

    @only_python3
    def test_function_def3(self):
        code = ("#bla\n"
                "@dec1\n"
                "def f(x, y=2, *z, **w) -> 'teste':\n"
                "    pass")
        nodes = get_nodes(code, ast.FunctionDef)
        self.assertPosition(nodes[0], (2, 0), (4, 8), (3, 3))

    def test_function_def4(self):
        code = ("#bla\n"
                "def g(x):\n"
                "    return x\n"
                "@g\n"
                "def f():\n"
                "    pass")
        nodes = get_nodes(code, ast.FunctionDef)
        self.assertPosition(nodes[0], (2, 0), (3, 12), (2, 3))
        self.assertPosition(nodes[1], (4, 0), (6, 8), (5, 3))

    @only_python35
    def test_async_function_def(self):
        code = ("#bla\n"
                "async def f(x, y=2, *z, **w):\n"
                "    pass")
        nodes = get_nodes(code, ast.AsyncFunctionDef)
        self.assertPosition(nodes[0], (2, 0), (3, 8), (2, 5))
