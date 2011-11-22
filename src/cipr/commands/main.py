from fabric.main import main as fab_main
from os import path
import sys

def main():
    dir = path.join(path.abspath(path.dirname(__file__)), 'fabfile')
    sys.argv.extend(['-f', dir])
    fab_main()
  