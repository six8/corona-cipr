from fabric.api import local, task, abort, settings
from clom import clom

@task
def release():
    """
    Release current version to pypi
    """

    with settings(warn_only=True):
        r = local(clom.git['diff-files']('--quiet', '--ignore-submodules', '--'))

    if r.return_code != 0:
        abort('There are uncommitted changes, commit or stash them before releasing')

    version = open('VERSION.txt').read().strip()

    print('Releasing %s...' % version)
    local(clom.git.flow.release.start(version))
    local(clom.git.flow.release.finish(version, m='Release-%s' % version))
    local(clom.git.push('origin', 'master', 'develop', tags=True))
    local(clom.python('setup.py', 'sdist', 'upload'))

@task
def register():
    """
    Register current version to pypi
    """
    local(clom.python('setup.py', 'register'))   