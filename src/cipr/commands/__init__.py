from fabric.api import *
from os import path
import os
import shutil
from clom import clom
import json
import tempfile

env.base_dir = path.dirname(path.abspath(path.dirname(__file__)))
env.skel_dir = path.join(env.base_dir, 'skel')
env.package_dir = os.getenv('CIPR_PACKAGES', None) or path.expanduser('~/.cipr/packages')
env.dir = path.abspath(os.getcwd())

class Package(object):
    def __init__(self, dir):
        self._dir = dir
        self._packagesDir = path.dirname(dir)
        self.info = {}

        name = path.basename(self._dir)
        if name.endswith('.git'):
            self.name = path.splitext(path.basename(name))[0]
        else:
            self.name = path.basename(name)

        info_file = path.join(self._dir, 'info.json')
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
                for name in self.install_requires
        ]

    @property
    def install_requires(self):
        return self.info.get('install_requires', [])

class CiprCfg(object):
    def __init__(self, ciprfile):
        self._filename = ciprfile
        self._data = {}
        if path.exists(self._filename):
            with open(self._filename) as file:
                self._data = json.load(file)

    def _save(self):
        data = json.dumps(self._data, indent=2)
        with open(self._filename, 'w') as file:
            file.write(data)

    @property
    def packages(self):
        """
        Returns a list of packages available to this project
        """
        return self._data.get('packages', None)

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

@task
def init(dir=None):
    """
    Initialize a Corona project directory.
    """
    if not dir:
        dir = env.dir
    env.dir = dir

    cfg = CiprCfg(path.join(env.dir, '.ciprcfg'))
    cfg._save()
    
    templ_dir = path.join(env.skel_dir, 'default')

    print('Copying files from %s' % templ_dir)
    for filename in os.listdir(templ_dir):
        src = path.join(templ_dir, filename)
        dst = path.join(dir, filename)
        if not path.exists(dst):
            shutil.copy(src, dst)

@task
def update(dir=None):
    if not dir:
        dir = env.dir
    env.dir = dir

    files = [path.join(dir, 'cipr.lua')]
    for filename in files:
        if path.exists(filename):
            os.remove(filename)
    init(dir)

@task
def uninstall(name):
    """
    Remove a package
    """
    package_dir = path.join(env.package_dir, name)
    if path.exists(package_dir):
        print('Removing %s...' % name)
        if path.islink(package_dir):
            os.remove(package_dir)
        else:
            shutil.rmtree(package_dir)

@task
def upgrade(package):
    if package.startswith('git'):
        name = path.splitext(path.basename(package))[0]
    else:
        name = path.basename(package)

    uninstall(name)
    install(package)

@task
def install(package):
    """
    Install a package from github and make it available for use.
    """
    if not path.exists(env.package_dir):
        os.makedirs(env.package_dir)

    if package.startswith('git'):
        name = path.splitext(path.basename(package))[0]
    else:
        name = path.basename(package)
        
    package_dir = path.join(env.package_dir, name)
    if path.exists(package_dir):
        print('Package %s already exists' % name)
        return
    else:
        print('Installing %s...' % name)


    if package.startswith('git'):
        tmpdir = tempfile.mkdtemp(prefix='cipr')
        local(clom.git.clone(package, tmpdir))
        project_dir = path.join(tmpdir, name)
        if path.exists(project_dir):
            shutil.move(tmpdir, package_dir)
        else:
            os.makedirs(package_dir)
            shutil.move(tmpdir, path.join(package_dir, name))

    elif path.exists(package):
        # Local
        os.symlink(package, package_dir)

    package = Package(package_dir)
    for require in package.install_requires:
        install(require)

@task
def add(name):
    """
    Add an installed package for use in this project
    """
    cfg = CiprCfg(path.join(env.dir, '.ciprcfg'))
    cfg.add_package(Package(path.join(env.package_dir, name)))

@task
def run():
    os.putenv('CIPR_PACKAGES', env.package_dir)
    os.putenv('CIPR_PROJECT', env.dir)
    local("'/Applications/CoronaSDK/Corona Terminal' '%s'" % env.dir, capture=False)

    