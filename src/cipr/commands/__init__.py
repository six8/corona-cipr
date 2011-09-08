from fabric.api import *
from os import path
import os
import shutil

env.base_dir = path.dirname(path.abspath(path.dirname(__file__)))
env.skel_dir = path.join(env.base_dir, 'skel')

@task
def init(dir=None):
    """
    Initialize a Corona project directory.
    """
    if not dir:
        dir = path.abspath(os.getcwd())

    templ_dir = path.join(env.skel_dir, 'default')

    print('Copying files from %s' % templ_dir)
    for filename in os.listdir(templ_dir):
        shutil.copy(path.join(templ_dir, filename), dir)