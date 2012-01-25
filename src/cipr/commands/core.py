from os import path
import os
import shutil
from clom import clom, AND
import json
import tempfile
import shutil
from glob import glob
from cipr.commands.cfg import Package, CiprCfg
from cipr.commands import env, util
from cipr.commands import app


@app.command
def init(ciprcfg, env, console):
    """
    Initialize a Corona project directory.
    """
    ciprcfg.create()
    
    templ_dir = path.join(env.skel_dir, 'default')

    console.quiet('Copying files from %s' % templ_dir)
    for src, dst in util.sync_dir_to(templ_dir, env.project_directory, ignore_existing=True):
        console.quiet('  %s -> %s' % (src, dst))

    src = path.join(env.code_dir, 'cipr.dev.lua')
    dst = path.join(env.project_directory, 'cipr.lua')
    console.quiet('  %s -> %s' % (src, dst))

    shutil.copy(src, dst)

@app.command
def update(env):
    """
    Update an existing cipr project to the latest intalled version.
    """
    files = [path.join(env.project_directory, 'cipr.lua')]
    for filename in files:
        if path.exists(filename):
            os.remove(filename)
    app.command.run(['init', env.project_directory])

@app.command(usage='[options] PACKAGE [PACKAGE...]')
def uninstall(args, env, console, ciprcfg):
    """
    Remove a package
    """
    for name in args:
        package_dir = path.join(env.package_dir, name)
        if path.exists(package_dir):
            console.quiet('Removing %s...' % name)
            if path.islink(package_dir):
                os.remove(package_dir)
            else:
                shutil.rmtree(package_dir)

        ciprcfg.remove_package(name)


def _package_info(package):
    version = None
    type = 'dir'
    if package.startswith('git'):
        if '@' in package:
            package, version = package.split('@', 1)

        name = path.splitext(path.basename(package))[0]
        type = 'git'
    else:
        package = path.abspath(package)
        name = path.basename(package)

    return package, name, version, type


@app.command(
    opts=(app.opt('-u', '--upgrade', action='store_true', dest='upgrade', help='Force upgrade of installed package')),
    usage='[options] [PACKAGE] [PACKAGE...]'
)
def install(args, console, env, ciprcfg, opts):
    """
    Install a package from github and make it available for use.
    """
    if len(args) == 0:
        # Is this a cipr project?
        if ciprcfg.exists:
            # Install all the packages for this project
            console.quiet('Installing current project packages...')
            for name, source in ciprcfg.packages.items():
                if opts.upgrade:
                    app.command.run(['install', '--upgrade', source])
                else:
                    app.command.run(['install', source])
        else:
            console.error('No cipr project or package found.')
        return
    else:
        for source in args:
            package, name, version, type = _package_info(source)

            if not path.exists(env.package_dir):
                os.makedirs(env.package_dir)

            package_dir = path.join(env.package_dir, name)

            if path.exists(package_dir):
                if opts.upgrade:
                    app.command.run(['uninstall', name])
                else:
                    console.quiet('Package %s already exists. Use --upgrade to force a re-install.' % name)
                    return

            console.quiet('Installing %s...' % name)


            if type == 'git':        
                tmpdir = tempfile.mkdtemp(prefix='cipr')
                clom.git.clone(package, tmpdir).shell.execute()

                if version:
                    cmd = AND(clom.cd(tmpdir), clom.git.checkout(version))
                    cmd.shell.execute()

                package_json = path.join(tmpdir, 'package.json')
                if path.exists(package_json):
                    # Looks like a cipr package, copy directly
                    shutil.move(tmpdir, package_dir)
                else:
                    # Not a cipr package, sandbox in sub-directory
                    shutil.move(tmpdir, path.join(package_dir, name))

                console.quiet('`%s` installed from git repo to `%s`' % (name, package_dir))

            elif path.exists(package):
                # Local        
                os.symlink(package, package_dir)
            else:
                console.error('Package `%s` type not recognized' % package)
                return
            
            pkg = Package(package_dir, source)
            ciprcfg.add_package(pkg)

            if pkg.dependencies:
                console.quiet('Installing dependancies...')
                for name, require in pkg.dependencies.items():
                    if opts.upgrade:
                        app.command.run(['install', '--upgrade', require])
                    else:
                        app.command.run(['install', require])

@app.command(opts=(app.opt('-l', '--long', action='store_true', dest='long_details', help='List details about package')))
def packages(ciprcfg, env, opts, console):
    """
    List installed packages for this project
    """
    for name, source in ciprcfg.packages.items():
        console.normal('- %s' % name)

        if opts.long_details:
            console.normal('  - directory: %s' % path.join(env.package_dir, name))        
            console.normal('  - source: %s' % source)        
            
    
@app.command
def run(env):
    """
    Run current project in the Corona Simulator
    """
    os.putenv('CIPR_PACKAGES', env.package_dir)
    os.putenv('CIPR_PROJECT', env.project_directory)
    cmd = clom['/Applications/CoronaSDK/Corona Terminal'](env.project_directory)

    try:
        cmd.shell.execute()
    except KeyboardInterrupt:
        pass

@app.command
def build(env, ciprcfg, console):
    """
    Build the current project for distribution
    """
    os.putenv('CIPR_PACKAGES', env.package_dir)
    os.putenv('CIPR_PROJECT', env.project_directory)
        
    if path.exists(env.build_dir):
        shutil.rmtree(env.build_dir)
        
    os.makedirs(env.build_dir)
        
    if not path.exists(env.dist_dir):
        os.makedirs(env.dist_dir)

    for src, dst in util.sync_dir_to(env.project_directory, env.build_dir, exclude=['.cipr', '.git', 'build', 'dist']):
        console.quiet('  %s -> %s' % (src, dst))
    
    for package in ciprcfg.packages.keys():
        for src, dst in util.sync_lua_dir_to(path.join(env.package_dir, package), env.build_dir, exclude=['.git'], include=['*.lua']):
            console.quiet('  %s -> %s' % (src, dst))        
    
    src = path.join(env.code_dir, 'cipr.lua')
    dst = path.join(env.build_dir, 'cipr.lua')
    shutil.copy(src, dst)
        
    cmd = AND(clom.cd(env.build_dir), clom['/Applications/CoronaSDK/Corona Terminal'](env.build_dir))

    console.normal('Be sure to output your app to %s' % env.dist_dir)
    
    try:
        cmd.shell.execute()
    except KeyboardInterrupt:
        pass
        
@app.command 
def packageipa(env, console):    
    """
    Package the built app as an ipa for distribution in iOS App Store
    """
    filenames = glob(path.join(env.dist_dir, '*.app'))
    filename, ext = path.splitext(path.basename(filenames[0]))
    ipa_name = filename + '.ipa'
    output_dir = path.dirname(env.dist_dir)
    ipa_path = path.join(output_dir, ipa_name)
    
    if path.exists(ipa_path):
        console.quiet('Removing %s' % ipa_path)
        os.remove(ipa_path)
        
    cmd = AND(clom.cd(output_dir), clom.zip(r=ipa_name).with_args('Payload/%s.app' % filename))
    cmd.shell.execute()


    console.quiet('Packaged %s' % ipa_path)

@app.command 
def expanddotpaths(env, console):        
    """
    Move files with dots in them to sub-directories
    """
    for filepath in os.listdir(path.join(env.dir)):
        filename, ext = path.splitext(filepath)
        if ext == '.lua' and '.' in filename:
            paths, newfilename = filename.rsplit('.', 1)
            newpath = paths.replace('.', '/')
            newfilename = path.join(newpath, newfilename) + ext

            console.quiet('Move %s to %s' % (filepath, newfilename))

            fullpath = path.join(env.project_directory, newpath)
            if not path.exists(fullpath):
                os.makedirs(fullpath)

            clom.git.mv(filepath, newfilename).shell.execute()


