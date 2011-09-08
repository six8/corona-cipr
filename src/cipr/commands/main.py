from fabric.main import main as fab_main
from os import path
import sys

def main():
    sys.argv.extend(['-f', path.abspath(path.join(path.dirname(__file__), '__init__.py'))])
    fab_main()
  