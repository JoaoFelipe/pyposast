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
