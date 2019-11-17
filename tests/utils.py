# Copyright (c) 2017 Universidade Federal Fluminense (UFF)
# This file is part of PyPosAST.
# Please, consult the license terms in the LICENSE file.
"""Base TestCase"""
# pylint: disable=unused-import

from __future__ import (absolute_import, division)

import unittest


from pyposast.cross_version import only_python2, only_python3
from pyposast.cross_version import only_python35, only_python36
from pyposast.cross_version import only_python38
from pyposast import get_nodes


class NodeTestCase(unittest.TestCase):
    """Base test case"""
    # pylint: disable=invalid-name

    def assertPosition(self, node, first, last, uid, messages=None):
        """Check node positions"""
        # pylint: disable=no-self-use
        node_first = (node.first_line, node.first_col)
        node_last = (node.last_line, node.last_col)
        messages = messages or []
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

    def assertOperation(self, node, first, last, uid, kind):
        messages = []
        if not node.kind == kind:
            messages.append(
                'kind does not match: {} != {}'.format(node.kind, kind)
            )
        self.assertPosition(node, first, last, uid, messages=messages)
        

    def assertNoBeforeInnerAfter(self, node):
        """Check if node does not have pos_before, pos_inner, pos_after"""
        self.assertFalse(hasattr(node, 'pos_before'))
        self.assertFalse(hasattr(node, 'pos_inner'))
        self.assertFalse(hasattr(node, 'pos_after'))

    def assertSimpleInnerPosition(self, node, first, last):
        """Check pos_before, pos_inner, pos_after"""
        node_first = (node.first_line, node.first_col)
        node_last = (node.last_line, node.last_col)
        self.assertPosition(node.pos_before, node_first, first, first)
        self.assertPosition(node.pos_inner, first, last, last)
        self.assertPosition(node.pos_after, last, node_last, node_last)
