from os import path
import os

__all__ = ['env']

class _Env:
	base_dir = path.dirname(path.dirname(path.abspath(__file__)))
	skel_dir = path.join(base_dir, 'skel')
	code_dir = path.join(base_dir, 'code')
	package_dir = os.getenv('CIPR_PACKAGES', None) or path.expanduser('~/.cipr/packages')
	dir = path.abspath(os.getcwd())
	dist_dir = path.join(dir, '..', 'dist', 'Payload')
	build_dir = path.join(dir, '..', 'build')

env = _Env()