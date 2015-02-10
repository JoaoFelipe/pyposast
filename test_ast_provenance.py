import unittest
import ast

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


class TestProvenanceVisitor(unittest.TestCase):

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


if __name__ == '__main__':
    unittest.main()

