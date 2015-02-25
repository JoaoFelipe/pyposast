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
        messages = []
        if not node_first == first:
            messages.append(
                'first does not match: {} != {}'.format(node_first, first))
        if not node_last == last:
            messages.append(
                'last does not match: {} != {}'.format(node_last, last))
        if not node.uid == uid:
            messages.append(
                'uid does not match: {} != {}'.format(node.uid, uid))
        if messages:
            raise AssertionError('\n'.join(messages))

    def test_name(self):
        code = ("#bla\n"
                "abc")
        nodes = get_nodes(code, ast.Name)
        self.assertPosition(nodes[0], (2, 0), (2, 3), (2, 3))

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
        self.assertPosition(nodes[0], (2, 1), (4, 5), (4, 5))

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

    def test_index(self):
        code = ("#bla\n"
                "a[1]")
        nodes = get_nodes(code, ast.Index)
        self.assertPosition(nodes[0], (2, 2), (2, 3), (2, 3))

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

    def test_tuple(self):
        code = ("#bla\n"
                "(\n"
                "1, 2,\n"
                "3\n"
                ")")
        nodes = get_nodes(code, ast.Tuple)
        self.assertPosition(nodes[0], (3, 0), (4, 1), (3, 1))

    def test_tuple2(self):
        code = ("#bla\n"
                "(\n"
                ")")

        nodes = get_nodes(code, ast.Tuple)
        self.assertPosition(nodes[0], (2, 0), (3, 1), (3, 1))

    def _test_tuple3(self):
        code = ("#bla\n"
                "(((0),\n"
                "1, 2,\n"
                "3\n"
                "))")
        nodes = get_nodes(code, ast.Tuple)
        self.assertPosition(nodes[0], (2, 2), (4, 1), (2, 5))

    def test_tuple4(self):
        code = ("#bla\n"
                "1,")
        nodes = get_nodes(code, ast.Tuple)
        self.assertPosition(nodes[0], (2, 0), (2, 1), (2, 1))

    def test_tuple5(self):
        code = ("#bla\n"
                "([1, 2], 3)")
        nodes = get_nodes(code, ast.Tuple)
        self.assertPosition(nodes[0], (2, 1), (2, 10), (2, 7))

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
        self.assertPosition(nodes[0], (2, 1), (5, 1), (5, 1))

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

    def test_yield(self):
        code = ("#bla\n"
                "yield   2")
        nodes = get_nodes(code, ast.Yield)
        self.assertPosition(nodes[0], (2, 0), (2, 9), (2, 5))

    def test_comprehension(self):
        code = ("#bla\n"
                "[x\n"
                " for x in l\n"
                " if x]")
        nodes = get_nodes(code, ast.comprehension)
        self.assertPosition(nodes[0], (3, 1), (4, 5), (3, 4))

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

    def test_set_comp(self):
        code = ("#bla\n"
                "{x\n"
                " for x in l\n"
                " if x}")
        nodes = get_nodes(code, ast.SetComp)
        self.assertPosition(nodes[0], (2, 0), (4, 6), (4, 6))

    def test_list_comp(self):
        code = ("#bla\n"
                "[x\n"
                " for x in l\n"
                " if x]")
        nodes = get_nodes(code, ast.ListComp)
        self.assertPosition(nodes[0], (2, 0), (4, 6), (4, 6))

    def test_set(self):
        code = ("#bla\n"
                "{x,\n"
                " 1,\n"
                " 3}")
        nodes = get_nodes(code, ast.Set)
        self.assertPosition(nodes[0], (2, 0), (4, 3), (4, 3))

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


if __name__ == '__main__':
    unittest.main()

#ToDO: test_tuple3

