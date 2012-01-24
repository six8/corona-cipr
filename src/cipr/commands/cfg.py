from os import path
import os
import json

class Package(object):    
    def __init__(self, dir):
        self._dir = dir
        self._packagesDir = path.dirname(dir)
        self.info = {}

        self.name = path.basename(self._dir)

        info_file = path.join(self._dir, 'package.json')
        if path.exists(info_file):
            with open(info_file) as file:
                self.info = json.load(file)

    @property
    def path(self):
        return self._dir

    @property
    def deploy_packages(self):
        return [
            Package(path.join(self._packagesDir, name))
                for name in self.dependencies.keys()
        ]

    @property
    def dependencies(self):
        return self.info.get('dependencies', {})

class CiprCfg(object):
    """
    Manages a projects .ciprcfg file.
    """
    def __init__(self, ciprfile):
        self._filename = ciprfile
        self._data = {}
        if path.exists(self._filename):
            with open(self._filename) as file:
                self._data = json.load(file)

    def create(self):
        dir = path.dirname(self._filename)
        if not path.exists(dir):
            os.makedirs(dir)

        self._save()

    def _save(self):
        data = json.dumps(self._data, indent=2)
        with open(self._filename, 'w') as file:
            file.write(data)

    @property
    def packages(self):
        """
        Returns a list of packages available to this project
        """
        return self._data.get('packages', [])

    def add_package(self, package):
        """
        Add a package to this project
        """
        self._data.setdefault('packages', [])
        if package.name not in self._data['packages']:
            self._data['packages'].append(package.name)

            for package in package.deploy_packages:
                self.add_package(package)

            self._save()