import clik
from os import path
import os
from optparse import make_option as opt
from cipr.commands.cfg import CiprCfg
from cipr.commands import env


def _args(opts):
    env.project_directory = opts.project_directory

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