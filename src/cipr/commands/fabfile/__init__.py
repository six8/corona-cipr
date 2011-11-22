from __future__ import absolute_import
from fabric.api import *
from os import path
import os

from fabfile.core import *
from fabfile import image

env.base_dir = path.dirname(path.dirname(path.abspath(path.dirname(__file__))))
env.skel_dir = path.join(env.base_dir, 'skel')
env.code_dir = path.join(env.base_dir, 'code')
env.package_dir = os.getenv('CIPR_PACKAGES', None) or path.expanduser('~/.cipr/packages')
env.dir = path.abspath(os.getcwd())
env.dist_dir = path.join(env.dir, '..', 'dist', 'Payload')
env.build_dir = path.join(env.dir, '..', 'build')