from fabric.api import *
from os import path
import os
import shutil
from clom import clom, AND
import json
import tempfile
import shutil
from fabfile import util
from glob import glob

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

    src = path.join(env.code_dir, 'cipr.dev.lua')
    dst = path.join(dir, 'cipr.lua')
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
        package = path.abspath(package)
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

    if package.install_requires:
        print('Installing dependancies...')
        for require in package.install_requires:
            install(require)

@task
def add(*names):
    """
    Add an installed package for use in this project
    """
    found_dirs = []
    missing = []
    for name in names:
        dir = path.join(env.package_dir, name)
        if path.exists(dir):
            found_dirs.append((name, dir))
        else:
            missing.append(name)

    if missing:
        abort('Could not find packages "%s", please `cipr install` them.' % '", "'.join(missing))            
    else:
        cfg = CiprCfg(path.join(env.dir, '.ciprcfg'))
        
        for name, dir in found_dirs:
            print('Adding packge %r to project' % name)            
            cfg.add_package(Package(dir))

@task
def list(switches=''):
    """
    List installed packages
    """
    for name in os.listdir(env.package_dir):
        if 'l' in switches:
            print('- %s\t%s' % (name, env.package_dir))
        else:
            print('- %s' % name)
    
@task
def run():
    os.putenv('CIPR_PACKAGES', env.package_dir)
    os.putenv('CIPR_PROJECT', env.dir)
    local("'/Applications/CoronaSDK/Corona Terminal' '%s'" % env.dir, capture=False)

@task
def build():
    os.putenv('CIPR_PACKAGES', env.package_dir)
    os.putenv('CIPR_PROJECT', env.dir)
        
    if path.exists(env.build_dir):
        shutil.rmtree(env.build_dir)
        
    os.makedirs(env.build_dir)
    
    util.sync_dir_to(env.dir, env.build_dir, exclude=['.ciprcfg', '.git'])
    
    cfg = CiprCfg(path.join(env.dir, '.ciprcfg'))
    for package in cfg.packages:
        util.sync_lua_dir_to(path.join(env.package_dir, package), env.build_dir, exclude=['.git'], include=['*.lua'])
    
    src = path.join(env.code_dir, 'cipr.lua')
    dst = path.join(env.build_dir, 'cipr.lua')
    shutil.copy(src, dst)
        
    cmd = AND(clom.cd(env.build_dir), clom['/Applications/CoronaSDK/Corona Terminal'](env.build_dir))
    local(cmd, capture=False)
        
@task    
def packageipa():    
    filenames = glob(path.join(env.dist_dir, '*.app'))
    filename, ext = path.splitext(path.basename(filenames[0]))
    ipa_name = filename + '.ipa'
    output_dir = path.dirname(env.dist_dir)
    ipa_path = path.join(output_dir, ipa_name)
    
    if path.exists(ipa_path):
        print('Removing %s' % ipa_path)
        os.remove(ipa_path)
        
    local('cd "{dir}" && zip -r "{ipa_name}" "Payload/{filename}.app"'.format(dir=output_dir, ipa_name=ipa_name, filename=filename), capture=False)
    
    print('Packaged %s' % ipa_path)

@task    
def expanddotpaths():        
    for filepath in os.listdir(path.join(env.dir)):
        filename, ext = path.splitext(filepath)
        if ext == '.lua' and '.' in filename:
            paths, newfilename = filename.rsplit('.', 1)
            newpath = paths.replace('.', '/')
            newfilename = path.join(newpath, newfilename) + ext

            print('Move %s to %s' % (filepath, newfilename))

            fullpath = path.join(env.dir, newpath)
            if not path.exists(fullpath):
                os.makedirs(fullpath)

            local(clom.git.mv(filepath, newfilename))


