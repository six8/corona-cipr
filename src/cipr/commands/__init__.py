from os import path
import os

__all__ = ['env']

class _Env:
    base_dir = path.dirname(path.dirname(path.abspath(__file__)))
    skel_dir = path.join(base_dir, 'skel')
    code_dir = path.join(base_dir, 'code')
    project_directory = path.abspath(os.getcwd())    

    @property
    def package_dir(self):
        return os.getenv('CIPR_PACKAGES', None) or path.join(self.project_directory, '.cipr/packages')    

    @property
    def dist_dir(self):
        return path.abspath(path.join(self.project_directory, 'dist'))

    @property
    def build_dir(self):
        return path.abspath(path.join(self.project_directory, 'build'))

env = _Env()