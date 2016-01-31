# Copyright (c) 2016 Universidade Federal Fluminense (UFF)
# This file is part of PyPosAST.
# Please, consult the license terms in the LICENSE file.

import sys

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO


def select_version(compare_func):
	def only_version_x(fn):
		def inner(*args, **kwargs):
			if compare_func(sys.version_info):
				return fn(*args, **kwargs)
			return None
		return inner
	return only_version_x

only_python2 = select_version(lambda x: x < (3, 0))
only_python3 = select_version(lambda x: x >= (3, 0))
only_python35 = select_version(lambda x: x >= (3, 5))


def buffered_str(text, encoding="utf-8"):
	ver = sys.version_info
	if ver >= (3, 0) and isinstance(text, bytes):
		return text.decode(encoding)
	if ver < (3, 0) and isinstance(text, unicode):
		return text.encode('ascii', 'replace')
	return text
