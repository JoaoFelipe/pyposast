import unittest
import ast
import sys

from ast_provenance import ProvenanceVisitor as Visitor


PATH = "__main__"


class GetVisitor(ast.NodeVisitor):

    def __init__(self, tree, desired_type):
        self.desired_type = desired_type
        self.result = []
        self.visit(tree)

    def generic_visit(self, node):
        if isinstance(node, self.desired_type):
            self.result.append(node)
        return ast.NodeVisitor.generic_visit(self, node)


def get_nodes(code, desired_type):
    return GetVisitor(Visitor(code, PATH).tree, desired_type).result

def only_python2(fn):
    def decorator(*args, **kwargs):
        if sys.version_info < (3, 0):
            return fn(*args, **kwargs)
        return None
    return decorator


class TestProvenanceVisitor(unittest.TestCase):

    def assertPosition(self, node, first, last, uid):
        node_first = (node.first_line, node.first_col)
        node_last = (node.last_line, node.last_col)
        if not node_first == first:
            raise AssertionError(
                'first does not match: {} != {}'.format(node_first, first))
        if not node_last == last:
            raise AssertionError(
                'last does not match: {} != {}'.format(node_last, last))
        if not node.uid == uid:
            raise AssertionError(
                'uid does not match: {} != {}'.format(node.uid, uid))

    def test_name(self):
        code = ("#bla\n"
                "abc")
        nodes = get_nodes(code, ast.Name)
        name = nodes[0]
        self.assertEqual(name.first_line, 2)
        self.assertEqual(name.first_col, 0)
        self.assertEqual(name.last_line, 2)
        self.assertEqual(name.last_col, 3)
        self.assertEqual(name.uid, (2, 3))

    def test_num(self):
        code = ("#bla\n"
                "12")
        nodes = get_nodes(code, ast.Num)
        num = nodes[0]
        self.assertEqual(num.first_line, 2)
        self.assertEqual(num.first_col, 0)
        self.assertEqual(num.last_line, 2)
        self.assertEqual(num.last_col, 2)
        self.assertEqual(num.uid, (2, 2))

    @only_python2
    def test_num2(self):
        """ Python 3 Num uses the minus as unaryop, USub """
        code = ("#bla\n"
                "-  1245")
        nodes = get_nodes(code, ast.Num)
        num = nodes[0]
        self.assertEqual(num.first_line, 2)
        self.assertEqual(num.first_col, 0)
        self.assertEqual(num.last_line, 2)
        self.assertEqual(num.last_col, 7)
        self.assertEqual(num.uid, (2, 7))

    @only_python2
    def test_num3(self):
        """ Python 3 Num uses the minus as unaryop, USub """
        code = ("#bla\n"
                "-  0")
        nodes = get_nodes(code, ast.Num)
        num = nodes[0]
        self.assertEqual(num.first_line, 2)
        self.assertEqual(num.first_col, 0)
        self.assertEqual(num.last_line, 2)
        self.assertEqual(num.last_col, 4)
        self.assertEqual(num.uid, (2, 4))

    def test_num4(self):
        code = ("#bla\n"
                "0x1245")
        nodes = get_nodes(code, ast.Num)
        num = nodes[0]
        self.assertEqual(num.first_line, 2)
        self.assertEqual(num.first_col, 0)
        self.assertEqual(num.last_line, 2)
        self.assertEqual(num.last_col, 6)
        self.assertEqual(num.uid, (2, 6))

    def test_str(self):
        code = ("#bla\n"
                "'ab\\\n"
                " cd\\\n"
                " ef'")
        nodes = get_nodes(code, ast.Str)
        string = nodes[0]
        self.assertEqual(string.first_line, 2)
        self.assertEqual(string.first_col, 0)
        self.assertEqual(string.last_line, 4)
        self.assertEqual(string.last_col, 4)
        self.assertEqual(string.uid, (4, 4))

    def test_str2(self):
        code = ("#bla\n"
                "'abcd'")
        nodes = get_nodes(code, ast.Str)
        string = nodes[0]
        self.assertEqual(string.first_line, 2)
        self.assertEqual(string.first_col, 0)
        self.assertEqual(string.last_line, 2)
        self.assertEqual(string.last_col, 6)
        self.assertEqual(string.uid, (2, 6))

    def test_str3(self):
        code = ("#bla\n"
                "('ab'\\\n"
                " 'cd'\n"
                " 'ef')")
        nodes = get_nodes(code, ast.Str)
        string = nodes[0]
        self.assertEqual(string.first_line, 2)
        self.assertEqual(string.first_col, 1)
        self.assertEqual(string.last_line, 4)
        self.assertEqual(string.last_col, 5)
        self.assertEqual(string.uid, (4, 5))

    def test_str4(self):
        code = ("#bla\n"
                "'ab' 'cd' 'ef'")
        nodes = get_nodes(code, ast.Str)
        string = nodes[0]
        self.assertEqual(string.first_line, 2)
        self.assertEqual(string.first_col, 0)
        self.assertEqual(string.last_line, 2)
        self.assertEqual(string.last_col, 14)
        self.assertEqual(string.uid, (2, 14))

    def test_attribute(self):
        code = ("#bla\n"
                "a.b")
        nodes = get_nodes(code, ast.Attribute)
        attribute = nodes[0]
        self.assertEqual(attribute.first_line, 2)
        self.assertEqual(attribute.first_col, 0)
        self.assertEqual(attribute.last_line, 2)
        self.assertEqual(attribute.last_col, 3)
        self.assertEqual(attribute.uid, (2, 1))

    def test_attribute2(self):
        code = ("#bla\n"
                "a.\\\n"
                "b")
        nodes = get_nodes(code, ast.Attribute)
        attribute = nodes[0]
        self.assertEqual(attribute.first_line, 2)
        self.assertEqual(attribute.first_col, 0)
        self.assertEqual(attribute.last_line, 3)
        self.assertEqual(attribute.last_col, 1)
        self.assertEqual(attribute.uid, (2, 1))

    def test_attribute3(self):
        code = ("#bla\n"
                "a.b.c")
        nodes = get_nodes(code, ast.Attribute)
        attribute = nodes[0]
        self.assertEqual(attribute.first_line, 2)
        self.assertEqual(attribute.first_col, 0)
        self.assertEqual(attribute.last_line, 2)
        self.assertEqual(attribute.last_col, 5)
        self.assertEqual(attribute.uid, (2, 3))
        attribute2 = nodes[1]
        self.assertEqual(attribute2.first_line, 2)
        self.assertEqual(attribute2.first_col, 0)
        self.assertEqual(attribute2.last_line, 2)
        self.assertEqual(attribute2.last_col, 3)
        self.assertEqual(attribute2.uid, (2, 1))

    def test_attribute4(self):
        code = ("#bla\n"
                "a.\\\n"
                "b.c\\\n"
                ".d")
        nodes = get_nodes(code, ast.Attribute)
        attribute = nodes[0]
        self.assertEqual(attribute.first_line, 2)
        self.assertEqual(attribute.first_col, 0)
        self.assertEqual(attribute.last_line, 4)
        self.assertEqual(attribute.last_col, 2)
        self.assertEqual(attribute.uid, (4, 0))
        attribute2 = nodes[1]
        self.assertEqual(attribute2.first_line, 2)
        self.assertEqual(attribute2.first_col, 0)
        self.assertEqual(attribute2.last_line, 3)
        self.assertEqual(attribute2.last_col, 3)
        self.assertEqual(attribute2.uid, (3, 1))
        attribute3 = nodes[2]
        self.assertEqual(attribute3.first_line, 2)
        self.assertEqual(attribute3.first_col, 0)
        self.assertEqual(attribute3.last_line, 3)
        self.assertEqual(attribute3.last_col, 1)
        self.assertEqual(attribute3.uid, (2, 1))

    def test_index(self):
        code = ("#bla\n"
                "a[1]")
        nodes = get_nodes(code, ast.Index)
        index = nodes[0]
        self.assertEqual(index.first_line, 2)
        self.assertEqual(index.first_col, 2)
        self.assertEqual(index.last_line, 2)
        self.assertEqual(index.last_col, 3)
        self.assertEqual(index.uid, (2, 3))

    def test_ellipsis(self):
        code = ("#bla\n"
                "a[...]")
        nodes = get_nodes(code, ast.Ellipsis)
        ellipsis = nodes[0]
        self.assertEqual(ellipsis.first_line, 2)
        self.assertEqual(ellipsis.first_col, 2)
        self.assertEqual(ellipsis.last_line, 2)
        self.assertEqual(ellipsis.last_col, 5)
        self.assertEqual(ellipsis.uid, (2, 5))

    @only_python2
    def test_ellipsis2(self):
        """ Invalid Python 3 syntax """
        code = ("#bla\n"
                "a[.\\\n"
                "..]")
        nodes = get_nodes(code, ast.Ellipsis)
        ellipsis = nodes[0]
        self.assertEqual(ellipsis.first_line, 2)
        self.assertEqual(ellipsis.first_col, 2)
        self.assertEqual(ellipsis.last_line, 3)
        self.assertEqual(ellipsis.last_col, 2)
        self.assertEqual(ellipsis.uid, (3, 2))

    def test_slice(self):
        code = ("#bla\n"
                "a[1:2:3]")
        nodes = get_nodes(code, ast.Slice)
        slice_node = nodes[0]
        self.assertEqual(slice_node.first_line, 2)
        self.assertEqual(slice_node.first_col, 2)
        self.assertEqual(slice_node.last_line, 2)
        self.assertEqual(slice_node.last_col, 7)
        self.assertEqual(slice_node.uid, (2, 4))

    def test_slice2(self):
        code = ("#bla\n"
                "a[:\\\n"
                "2:3]")
        nodes = get_nodes(code, ast.Slice)
        slice_node = nodes[0]
        self.assertEqual(slice_node.first_line, 2)
        self.assertEqual(slice_node.first_col, 2)
        self.assertEqual(slice_node.last_line, 3)
        self.assertEqual(slice_node.last_col, 3)
        self.assertEqual(slice_node.uid, (2, 3))

    def test_slice3(self):
        code = ("#bla\n"
                "a[:\\\n"
                ":2]")
        nodes = get_nodes(code, ast.Slice)
        slice_node = nodes[0]
        self.assertEqual(slice_node.first_line, 2)
        self.assertEqual(slice_node.first_col, 2)
        self.assertEqual(slice_node.last_line, 3)
        self.assertEqual(slice_node.last_col, 2)
        self.assertEqual(slice_node.uid, (2, 3))

    def test_slice4(self):
        code = ("#bla\n"
                "a[:]")
        nodes = get_nodes(code, ast.Slice)
        slice_node = nodes[0]
        self.assertEqual(slice_node.first_line, 2)
        self.assertEqual(slice_node.first_col, 2)
        self.assertEqual(slice_node.last_line, 2)
        self.assertEqual(slice_node.last_col, 3)
        self.assertEqual(slice_node.uid, (2, 3))

    def test_slice5(self):
        code = ("#bla\n"
                "a[::]")
        nodes = get_nodes(code, ast.Slice)
        slice_node = nodes[0]
        self.assertEqual(slice_node.first_line, 2)
        self.assertEqual(slice_node.first_col, 2)
        self.assertEqual(slice_node.last_line, 2)
        self.assertEqual(slice_node.last_col, 4)
        self.assertEqual(slice_node.uid, (2, 3))

    def test_slice6(self):
        code = ("#bla\n"
                "a[11:2\\\n"
                ":]")
        nodes = get_nodes(code, ast.Slice)
        slice_node = nodes[0]
        self.assertEqual(slice_node.first_line, 2)
        self.assertEqual(slice_node.first_col, 2)
        self.assertEqual(slice_node.last_line, 3)
        self.assertEqual(slice_node.last_col, 1)
        self.assertEqual(slice_node.uid, (2, 5))

    def test_ext_slice(self):
        code = ("#bla\n"
                "a[1:2,3]")
        nodes = get_nodes(code, ast.ExtSlice)
        slice_node = nodes[0]
        self.assertEqual(slice_node.first_line, 2)
        self.assertEqual(slice_node.first_col, 2)
        self.assertEqual(slice_node.last_line, 2)
        self.assertEqual(slice_node.last_col, 7)
        self.assertEqual(slice_node.uid, (2, 6))

    def test_ext_slice2(self):
        code = ("#bla\n"
                "a[1:2:,3]")
        nodes = get_nodes(code, ast.ExtSlice)
        slice_node = nodes[0]
        self.assertEqual(slice_node.first_line, 2)
        self.assertEqual(slice_node.first_col, 2)
        self.assertEqual(slice_node.last_line, 2)
        self.assertEqual(slice_node.last_col, 8)
        self.assertEqual(slice_node.uid, (2, 7))

    def test_ext_slice2(self):
        code = ("#bla\n"
                "a[3,1:2:]")
        nodes = get_nodes(code, ast.ExtSlice)
        slice_node = nodes[0]
        self.assertEqual(slice_node.first_line, 2)
        self.assertEqual(slice_node.first_col, 2)
        self.assertEqual(slice_node.last_line, 2)
        self.assertEqual(slice_node.last_col, 8)
        self.assertEqual(slice_node.uid, (2, 4))

    def test_subscript(self):
        code = ("#bla\n"
                "a\\\n"
                "[1]")
        nodes = get_nodes(code, ast.Subscript)
        subscript = nodes[0]
        self.assertEqual(subscript.first_line, 2)
        self.assertEqual(subscript.first_col, 0)
        self.assertEqual(subscript.last_line, 3)
        self.assertEqual(subscript.last_col, 3)
        self.assertEqual(subscript.uid, (3, 3))

    def test_subscript2(self):
        code = ("#bla\n"
                "a[\n"
                "1]")
        nodes = get_nodes(code, ast.Subscript)
        subscript = nodes[0]
        self.assertEqual(subscript.first_line, 2)
        self.assertEqual(subscript.first_col, 0)
        self.assertEqual(subscript.last_line, 3)
        self.assertEqual(subscript.last_col, 2)
        self.assertEqual(subscript.uid, (3, 2))

    def test_subscript3(self):
        code = ("#bla\n"
                "a[1:\n"
                "2,\n"
                "3 ]")
        nodes = get_nodes(code, ast.Subscript)
        subscript = nodes[0]
        self.assertEqual(subscript.first_line, 2)
        self.assertEqual(subscript.first_col, 0)
        self.assertEqual(subscript.last_line, 4)
        self.assertEqual(subscript.last_col, 3)
        self.assertEqual(subscript.uid, (4, 3))

    def test_tuple(self):
        code = ("#bla\n"
                "(\n"
                "1, 2,\n"
                "3\n"
                ")")
        nodes = get_nodes(code, ast.Tuple)
        tup = nodes[0]
        self.assertEqual(tup.first_line, 3)
        self.assertEqual(tup.first_col, 0)
        self.assertEqual(tup.last_line, 4)
        self.assertEqual(tup.last_col, 1)
        self.assertEqual(tup.uid, (3, 1))

    def test_tuple2(self):
        code = ("#bla\n"
                "(\n"
                ")")

        nodes = get_nodes(code, ast.Tuple)
        tup = nodes[0]
        self.assertEqual(tup.first_line, 2)
        self.assertEqual(tup.first_col, 0)
        self.assertEqual(tup.last_line, 3)
        self.assertEqual(tup.last_col, 1)
        self.assertEqual(tup.uid, (3, 1))

    def _test_tuple3(self):
        code = ("#bla\n"
                "(((0),\n"
                "1, 2,\n"
                "3\n"
                "))")
        nodes = get_nodes(code, ast.Tuple)
        tup = nodes[0]
        self.assertEqual(tup.first_line, 2)
        self.assertEqual(tup.first_col, 2)
        self.assertEqual(tup.last_line, 4)
        self.assertEqual(tup.last_col, 1)
        self.assertEqual(tup.uid, (2, 5))

    def test_tuple4(self):
        code = ("#bla\n"
                "1,")
        nodes = get_nodes(code, ast.Tuple)
        tup = nodes[0]
        self.assertEqual(tup.first_line, 2)
        self.assertEqual(tup.first_col, 0)
        self.assertEqual(tup.last_line, 2)
        self.assertEqual(tup.last_col, 1)
        self.assertEqual(tup.uid, (2, 1))

    def test_tuple5(self):
        code = ("#bla\n"
                "([1, 2], 3)")
        nodes = get_nodes(code, ast.Tuple)
        tup = nodes[0]
        self.assertEqual(tup.first_line, 2)
        self.assertEqual(tup.first_col, 1)
        self.assertEqual(tup.last_line, 2)
        self.assertEqual(tup.last_col, 10)
        self.assertEqual(tup.uid, (2, 7))

    def test_list(self):
        code = ("#bla\n"
                "[\n"
                "1, 2,\n"
                "3\n"
                "]")
        nodes = get_nodes(code, ast.List)
        lis = nodes[0]
        self.assertEqual(lis.first_line, 2)
        self.assertEqual(lis.first_col, 0)
        self.assertEqual(lis.last_line, 5)
        self.assertEqual(lis.last_col, 1)
        self.assertEqual(lis.uid, (5, 1))

    def test_list2(self):
        code = ("#bla\n"
                "[\n"
                "]")

        nodes = get_nodes(code, ast.List)
        lis = nodes[0]
        self.assertEqual(lis.first_line, 2)
        self.assertEqual(lis.first_col, 0)
        self.assertEqual(lis.last_line, 3)
        self.assertEqual(lis.last_col, 1)
        self.assertEqual(lis.uid, (3, 1))

    def test_list3(self):
        code = ("#bla\n"
                "([(0),\n"
                "1, 2,\n"
                "3\n"
                "])")
        nodes = get_nodes(code, ast.List)
        lis = nodes[0]
        self.assertEqual(lis.first_line, 2)
        self.assertEqual(lis.first_col, 1)
        self.assertEqual(lis.last_line, 5)
        self.assertEqual(lis.last_col, 1)
        self.assertEqual(lis.uid, (5, 1))

    @only_python2
    def test_repr(self):
        code = ("#bla\n"
                "`1`")
        nodes = get_nodes(code, ast.Repr)
        expr = nodes[0]
        self.assertEqual(expr.first_line, 2)
        self.assertEqual(expr.first_col, 0)
        self.assertEqual(expr.last_line, 2)
        self.assertEqual(expr.last_col, 3)
        self.assertEqual(expr.uid, (2, 3))

    @only_python2
    def test_repr2(self):
        code = ("#bla\n"
                "``1``")
        nodes = get_nodes(code, ast.Repr)
        expr = nodes[0]
        self.assertEqual(expr.first_line, 2)
        self.assertEqual(expr.first_col, 0)
        self.assertEqual(expr.last_line, 2)
        self.assertEqual(expr.last_col, 5)
        self.assertEqual(expr.uid, (2, 5))

    @only_python2
    def test_repr3(self):
        code = ("#bla\n"
                "``2\\\n"
                "``")
        nodes = get_nodes(code, ast.Repr)
        expr = nodes[0]
        self.assertEqual(expr.first_line, 2)
        self.assertEqual(expr.first_col, 0)
        self.assertEqual(expr.last_line, 3)
        self.assertEqual(expr.last_col, 2)
        self.assertEqual(expr.uid, (3, 2))

    def test_call(self):
        code = ("#bla\n"
                "fn(\n"
                "2)")
        nodes = get_nodes(code, ast.Call)
        expr = nodes[0]
        self.assertEqual(expr.first_line, 2)
        self.assertEqual(expr.first_col, 0)
        self.assertEqual(expr.last_line, 3)
        self.assertEqual(expr.last_col, 2)
        self.assertEqual(expr.uid, (3, 2))

    def test_call2(self):
        code = ("#bla\n"
                "fn(\n"
                "2)")
        nodes = get_nodes(code, ast.Call)
        expr = nodes[0]
        self.assertEqual(expr.first_line, 2)
        self.assertEqual(expr.first_col, 0)
        self.assertEqual(expr.last_line, 3)
        self.assertEqual(expr.last_col, 2)
        self.assertEqual(expr.uid, (3, 2))

    def test_call3(self):
        code = ("#bla\n"
                "fn\\\n"
                "((\n"
                "2, 3))")
        nodes = get_nodes(code, ast.Call)
        expr = nodes[0]
        self.assertEqual(expr.first_line, 2)
        self.assertEqual(expr.first_col, 0)
        self.assertEqual(expr.last_line, 4)
        self.assertEqual(expr.last_col, 6)
        self.assertEqual(expr.uid, (4, 6))

    def test_call4(self):
        code = ("#bla\n"
                "fn()\\\n"
                "((\n"
                "2, 3))")
        nodes = get_nodes(code, ast.Call)
        expr = nodes[0]
        self.assertEqual(expr.first_line, 2)
        self.assertEqual(expr.first_col, 0)
        self.assertEqual(expr.last_line, 4)
        self.assertEqual(expr.last_col, 6)
        self.assertEqual(expr.uid, (4, 6))
        expr = nodes[1]
        self.assertEqual(expr.first_line, 2)
        self.assertEqual(expr.first_col, 0)
        self.assertEqual(expr.last_line, 2)
        self.assertEqual(expr.last_col, 4)
        self.assertEqual(expr.uid, (2, 4))

    def test_compare(self):
        code = ("#bla\n"
                "2 < 3")
        nodes = get_nodes(code, ast.Compare)
        expr = nodes[0]
        self.assertEqual(expr.first_line, 2)
        self.assertEqual(expr.first_col, 0)
        self.assertEqual(expr.last_line, 2)
        self.assertEqual(expr.last_col, 5)
        self.assertEqual(expr.uid, (2, 5))

    def test_compare2(self):
        code = ("#bla\n"
                "2 < 3 <\\\n"
                " 5")
        nodes = get_nodes(code, ast.Compare)
        expr = nodes[0]
        self.assertEqual(expr.first_line, 2)
        self.assertEqual(expr.first_col, 0)
        self.assertEqual(expr.last_line, 3)
        self.assertEqual(expr.last_col, 2)
        self.assertEqual(expr.uid, (3, 2))

    def test_eq(self):
        code = ("#bla\n"
                "2 == 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertEqual(comp.first_line, 2)
        self.assertEqual(comp.first_col, 2)
        self.assertEqual(comp.last_line, 2)
        self.assertEqual(comp.last_col, 4)
        self.assertEqual(comp.uid, (2, 4))

    def test_not_eq(self):
        code = ("#bla\n"
                "2 != 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertEqual(comp.first_line, 2)
        self.assertEqual(comp.first_col, 2)
        self.assertEqual(comp.last_line, 2)
        self.assertEqual(comp.last_col, 4)
        self.assertEqual(comp.uid, (2, 4))

    def test_not_eq2(self):
        """ Python 2 syntax """
        code = ("#bla\n"
                "2 != 4\n"
                "5 != 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertEqual(comp.first_line, 2)
        self.assertEqual(comp.first_col, 2)
        self.assertEqual(comp.last_line, 2)
        self.assertEqual(comp.last_col, 4)
        self.assertEqual(comp.uid, (2, 4))
        comp2 = nodes[1].op_pos[0]
        self.assertEqual(comp2.first_line, 3)
        self.assertEqual(comp2.first_col, 2)
        self.assertEqual(comp2.last_line, 3)
        self.assertEqual(comp2.last_col, 4)
        self.assertEqual(comp2.uid, (3, 4))

    @only_python2
    def test_not_eq3(self):
        """ Python 2 syntax """
        code = ("#bla\n"
                "2 <> 4\n"
                "5 != 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertEqual(comp.first_line, 2)
        self.assertEqual(comp.first_col, 2)
        self.assertEqual(comp.last_line, 2)
        self.assertEqual(comp.last_col, 4)
        self.assertEqual(comp.uid, (2, 4))
        comp2 = nodes[1].op_pos[0]
        self.assertEqual(comp2.first_line, 3)
        self.assertEqual(comp2.first_col, 2)
        self.assertEqual(comp2.last_line, 3)
        self.assertEqual(comp2.last_col, 4)
        self.assertEqual(comp2.uid, (3, 4))

    def test_lt(self):
        code = ("#bla\n"
                "2 < 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertEqual(comp.first_line, 2)
        self.assertEqual(comp.first_col, 2)
        self.assertEqual(comp.last_line, 2)
        self.assertEqual(comp.last_col, 3)
        self.assertEqual(comp.uid, (2, 3))

    def test_lte(self):
        code = ("#bla\n"
                "2 <= 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertEqual(comp.first_line, 2)
        self.assertEqual(comp.first_col, 2)
        self.assertEqual(comp.last_line, 2)
        self.assertEqual(comp.last_col, 4)
        self.assertEqual(comp.uid, (2, 4))

    def test_gt(self):
        code = ("#bla\n"
                "2 > 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertEqual(comp.first_line, 2)
        self.assertEqual(comp.first_col, 2)
        self.assertEqual(comp.last_line, 2)
        self.assertEqual(comp.last_col, 3)
        self.assertEqual(comp.uid, (2, 3))

    def test_gte(self):
        code = ("#bla\n"
                "2 >= 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertEqual(comp.first_line, 2)
        self.assertEqual(comp.first_col, 2)
        self.assertEqual(comp.last_line, 2)
        self.assertEqual(comp.last_col, 4)
        self.assertEqual(comp.uid, (2, 4))

    def test_is(self):
        code = ("#bla\n"
                "2 is 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertEqual(comp.first_line, 2)
        self.assertEqual(comp.first_col, 2)
        self.assertEqual(comp.last_line, 2)
        self.assertEqual(comp.last_col, 4)
        self.assertEqual(comp.uid, (2, 4))

    def test_is_not(self):
        code = ("#bla\n"
                "2 is not 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertEqual(comp.first_line, 2)
        self.assertEqual(comp.first_col, 2)
        self.assertEqual(comp.last_line, 2)
        self.assertEqual(comp.last_col, 8)
        self.assertEqual(comp.uid, (2, 8))

    def test_in(self):
        code = ("#bla\n"
                "2 in 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertEqual(comp.first_line, 2)
        self.assertEqual(comp.first_col, 2)
        self.assertEqual(comp.last_line, 2)
        self.assertEqual(comp.last_col, 4)
        self.assertEqual(comp.uid, (2, 4))

    def test_not_in(self):
        code = ("#bla\n"
                "2 not in 4")
        nodes = get_nodes(code, ast.Compare)
        comp = nodes[0].op_pos[0]
        self.assertEqual(comp.first_line, 2)
        self.assertEqual(comp.first_col, 2)
        self.assertEqual(comp.last_line, 2)
        self.assertEqual(comp.last_col, 8)
        self.assertEqual(comp.uid, (2, 8))

    def test_yield(self):
        code = ("#bla\n"
                "yield   2")
        nodes = get_nodes(code, ast.Yield)
        expr = nodes[0]
        self.assertEqual(expr.first_line, 2)
        self.assertEqual(expr.first_col, 0)
        self.assertEqual(expr.last_line, 2)
        self.assertEqual(expr.last_col, 9)
        self.assertEqual(expr.uid, (2, 5))

    def test_comprehension(self):
        code = ("#bla\n"
                "[x\n"
                " for x in l\n"
                " if x]")
        nodes = get_nodes(code, ast.comprehension)
        comprehension = nodes[0]
        self.assertEqual(comprehension.first_line, 3)
        self.assertEqual(comprehension.first_col, 1)
        self.assertEqual(comprehension.last_line, 4)
        self.assertEqual(comprehension.last_col, 5)
        self.assertEqual(comprehension.uid, (3, 4))

    def test_generator_exp(self):
        code = ("#bla\n"
                "f(x\n"
                " for x in l\n"
                " if x)")
        nodes = get_nodes(code, ast.GeneratorExp)
        expr = nodes[0]
        self.assertEqual(expr.first_line, 2)
        self.assertEqual(expr.first_col, 2)
        self.assertEqual(expr.last_line, 4)
        self.assertEqual(expr.last_col, 5)
        self.assertEqual(expr.uid, (2, 3))

    def test_dict_comp(self):
        code = ("#bla\n"
                "{x:2\n"
                " for x in l\n"
                " if x}")
        nodes = get_nodes(code, ast.DictComp)
        expr = nodes[0]
        self.assertEqual(expr.first_line, 2)
        self.assertEqual(expr.first_col, 0)
        self.assertEqual(expr.last_line, 4)
        self.assertEqual(expr.last_col, 6)
        self.assertEqual(expr.uid, (4, 6))

    def test_set_comp(self):
        code = ("#bla\n"
                "{x\n"
                " for x in l\n"
                " if x}")
        nodes = get_nodes(code, ast.SetComp)
        expr = nodes[0]
        self.assertEqual(expr.first_line, 2)
        self.assertEqual(expr.first_col, 0)
        self.assertEqual(expr.last_line, 4)
        self.assertEqual(expr.last_col, 6)
        self.assertEqual(expr.uid, (4, 6))

    def test_list_comp(self):
        code = ("#bla\n"
                "[x\n"
                " for x in l\n"
                " if x]")
        nodes = get_nodes(code, ast.ListComp)
        expr = nodes[0]
        self.assertEqual(expr.first_line, 2)
        self.assertEqual(expr.first_col, 0)
        self.assertEqual(expr.last_line, 4)
        self.assertEqual(expr.last_col, 6)
        self.assertEqual(expr.uid, (4, 6))

    def test_set(self):
        code = ("#bla\n"
                "{x,\n"
                " 1,\n"
                " 3}")
        nodes = get_nodes(code, ast.Set)
        expr = nodes[0]
        self.assertEqual(expr.first_line, 2)
        self.assertEqual(expr.first_col, 0)
        self.assertEqual(expr.last_line, 4)
        self.assertEqual(expr.last_col, 3)
        self.assertEqual(expr.uid, (4, 3))

    def test_dict(self):
        code = ("#bla\n"
                "{}")
        nodes = get_nodes(code, ast.Dict)
        expr = nodes[0]
        self.assertEqual(expr.first_line, 2)
        self.assertEqual(expr.first_col, 0)
        self.assertEqual(expr.last_line, 2)
        self.assertEqual(expr.last_col, 2)
        self.assertEqual(expr.uid, (2, 2))

    def test_dict2(self):
        code = ("#bla\n"
                "{1}, {1: x,\n"
                "  2: 1,\n"
                "  3: 3}")
        nodes = get_nodes(code, ast.Dict)
        expr = nodes[0]
        self.assertEqual(expr.first_line, 2)
        self.assertEqual(expr.first_col, 5)
        self.assertEqual(expr.last_line, 4)
        self.assertEqual(expr.last_col, 7)
        self.assertEqual(expr.uid, (4, 7))


if __name__ == '__main__':
    unittest.main()

#ToDO: test_tuple3

