import clik
from os import path
import os
from optparse import make_option as opt
from cipr.commands.cfg import CiprCfg

class _Env(object):
    pass

def _args(opts):
    env = _Env()
    env.base_dir = path.dirname(path.dirname(path.abspath(__file__)))
    env.skel_dir = path.join(env.base_dir, 'skel')
    env.code_dir = path.join(env.base_dir, 'code')
    env.project_directory = opts.project_directory
    env.package_dir = os.getenv('CIPR_PACKAGES', None) or path.join(env.project_directory, '.cipr/packages')    
    env.dist_dir = path.join(env.project_directory, 'dist', 'Payload')
    env.build_dir = path.join(env.project_directory, 'build')

    return dict(
        env = env,
        ciprcfg = CiprCfg(path.join(env.project_directory, '.ciprcfg'))
    )

command = clik.App('cipr',
    version='0.8',
    description='Corona SDK package manager.',
    console_opts=True,
    conf_enabled=False,
    opts= opt('-d', '--project',
        dest='project_directory', default=path.abspath(os.getcwd()),
        help='Project directory'
    ),
    args_callback=_args
)