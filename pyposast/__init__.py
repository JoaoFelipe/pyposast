# Copyright (c) 2016 Universidade Federal Fluminense (UFF)
# This file is part of PyPosAST.
# Please, consult the license terms in the LICENSE file.

from __future__ import (absolute_import, division)

from .visitor import LineProvenanceVisitor

def parse(code, filename='<unknown>', mode='exec'):
	visitor = LineProvenanceVisitor(code, filename, mode)
	return visitor.tree
