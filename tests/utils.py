# Copyright (c) 2015 Universidade Federal Fluminense (UFF)
# This file is part of PyPosAST.
# Please, consult the license terms in the LICENSE file.

from __future__ import (absolute_import, division)

import unittest


from pyposast.cross_version import only_python2, only_python3, only_python35
from pyposast import get_nodes


class NodeTestCase(unittest.TestCase):

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
