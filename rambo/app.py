import click
import distutils
import errno
import json
import os
import pty
import shutil
import subprocess
import sys
import time
from distutils.dir_util import copy_tree
from distutils.errors import DistutilsFileError
from select import select
from subprocess import Popen
from threading import Thread

from rambo.providers import load_provider_keys
from rambo.scripts import install_lastpass
from rambo.utils import abort, get_user_home, set_env_var, get_env_var, dir_exists, dir_create, dir_delete, file_delete


## GLOBALS
# Create env var indicating where this code lives. This will be used latter by
# Vagrant as a check that the python cli is being used, as well as being a useful var.
PROJECT_LOCATION = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(PROJECT_LOCATION, 'settings.json'), 'r') as f:
    SETTINGS = json.load(f)
PROVIDERS = SETTINGS['PROVIDERS']
PROJECT_NAME = SETTINGS['PROJECT_NAME']

def write_to_log(data=None, file_name=None):
    '''Write data to log files. Will append data to a single combined log.
    Additionally write data to a log with a custom name (such as stderr)
    for any custom logs.

    Args:
        data (str or bytes): Data to write to log file.
        file_name (str): Used to create (or append to) an additional
                         log file with a custom name. Custom name always gets
                         `.log` added to the end.
    '''
    try:
        data = data.decode('utf-8')
    except AttributeError:
        pass # already a string

    data = ''.join([data.rstrip(), '\n']) # strip possible eol chars and add back exactly one

    dir_create(get_env_var('LOG_PATH'))
    fd_path = os.path.join(get_env_var('LOG_PATH'), 'history.log')
    fd = open(fd_path, 'a+')
    fd.write(data)
    fd.close()
    if file_name:
        fd_custom_path = os.path.join(get_env_var('LOG_PATH'), ''.join([file_name, '.log']))
        fd_custom = open(fd_custom_path, 'a+')
        fd_custom.write(data)
        fd_custom.close()

def _invoke_vagrant(cmd=None):
    '''Pass a command to vagrant. This outputs in near real-time,
    logs both stderr and stdout in a combined file, and detects stderr for
    our own error handling.

    Returns returncode (exitcode) of the command.

    Args:
        cmd (str): The cmd string that is appended to `vagrant ...`,
                   passed to the shell and executed.
    '''
    masters, slaves = zip(pty.openpty(), pty.openpty())
    cmd = ' '.join(['vagrant', cmd]).split()
    with Popen(cmd, stdin=slaves[0], stdout=slaves[0], stderr=slaves[1]) as p:
        for fd in slaves:
            os.close(fd) # no input
            readable = {
                masters[0]: sys.stdout.buffer, # store buffers seperately
                masters[1]: sys.stderr.buffer,
            }
        while readable:
            for fd in select(readable, [], [])[0]:
                try:
                    data = os.read(fd, 1024) # read available
                except OSError as e:
                    if e.errno != errno.EIO:
                        raise #XXX cleanup
                    del readable[fd] # EIO means EOF on some systems
                else:
                    if not data: # EOF
                        del readable[fd]
                    else:
                        if fd == masters[0]: # We caught stdout
                            click.echo(data.rstrip())
                            write_to_log(data)
                        else: # We caught stderr
                            click.echo(data.rstrip(), err=True)
                            write_to_log(data, 'stderr')
                        readable[fd].flush()
    for fd in masters:
        os.close(fd)
    return p.returncode

## Defs used by main cli cmd
def set_init_vars(cwd=None, tmpdir_path=None):
    '''Set custom environment variables that are always going to be needed by
    our custom Ruby code in the Vagrantfile chain.
    '''
    # env vars available to Python and Ruby
    set_env_var('ENV', PROJECT_LOCATION) # installed location of this code

    # effective CWD (likely real CWD, but may be changed by user.
    if cwd: # cli / api
        set_env_var('CWD', cwd)
    elif not get_env_var('CWD'): # Not previously set env var either
        try:
            set_env_var('CWD', os.getcwd())
        except FileNotFoundError:
            abort('Your current working directory no longer exists. '
                  'Did you delete it? Check for it with `ls ..`')

    # loc of tmpdir_path
    if tmpdir_path: # cli / api
        set_env_var('TMPDIR_PATH',
                    os.path.join(tmpdir_path, '.%s-tmp' % PROJECT_NAME))
    elif get_env_var('TMPDIR_PATH'): # Previously set env var
        set_env_var('TMPDIR_PATH',
                    os.path.join(get_env_var('TMPDIR_PATH'),
                                 '.%s-tmp' % PROJECT_NAME))
    else: # Not set, set to default loc
        set_env_var('TMPDIR_PATH',
                    os.path.join(os.getcwd(),
                                 '.%s-tmp' % PROJECT_NAME)) # default (cwd)
    set_env_var('LOG_PATH', os.path.join(get_env_var('TMPDIR_PATH'), 'logs'))

def set_vagrant_vars(vagrant_cwd=None, vagrant_dotfile_path=None):
    '''Set the environment varialbes prefixed with `VAGRANT_` that vagrant
    expects, and that we use, to modify some use paths.

    Agrs:
        vagrant_cwd (str): Location of `Vagrantfile`.
        vagrant_dotfile_path (str): Location of `.vagrant` metadata directory.
    '''
    # loc of Vagrantfile
    if vagrant_cwd: # cli / api
        os.environ["VAGRANT_CWD"] = vagrant_cwd
    elif 'VAGRANT_CWD' not in os.environ: # Not set in env var
        # if custom Vagrantfile exists in the default location.
        if os.path.isfile(os.path.join(os.getcwd(), 'Vagrantfile')):
            os.environ['VAGRANT_CWD'] = os.getcwd()
        else: # use default (installed) path
            os.environ['VAGRANT_CWD'] = PROJECT_LOCATION
    # loc of .vagrant dir
    if vagrant_dotfile_path: # cli / api
        os.environ['VAGRANT_DOTFILE_PATH'] = vagrant_dotfile_path
    elif 'VAGRANT_DOTFILE_PATH' not in os.environ: # Not set in env var
        os.environ['VAGRANT_DOTFILE_PATH'] = os.path.normpath(os.path.join(os.getcwd(), '.vagrant')) # default (cwd)

## Defs for cli subcommands
def createproject(ctx, project_name, project_path=None, config_only=None):
    '''Create project with basic configuration files.
    '''
    ## Create project dir
    if not project_path:
        project_path = os.getcwd()
    path = os.path.join(project_path, project_name)
    try:
        os.makedirs(path) # Make parent dirs if needed.
    except FileExistsError:
        abort('Directory already exists.')
    click.echo('Created %s project "%s" in %s.'
               % (PROJECT_NAME.capitalize(), project_name, project_path))
    ## Fill project dir with basic configs.
    if not config_only:
        export('saltstack', path)
        install_auth(path)


def destroy(ctx=None, vagrant_cwd=None, vagrant_dotfile_path=None):
    '''Destroy a VM / container and all its metadata. Default leaves logs.
    All str args can also be set as an environment variable; arg takes precedence.

    Agrs:
        ctx (object): Click Context object.
        vagrant_cwd (str): Location of `Vagrantfile`.
        vagrant_dotfile_path (str): Location of `.vagrant` metadata directory.
    '''
    # TODO add finding and deleting of all VMs registered to this installation.
    # TODO (optional) add finding and deleting of all VMs across all installations.
    # TODO add an --all flag to delete the whole .rambo-tmp dir. Default leaves logs.

    if not ctx: # Else handled by cli.
        set_init_vars()
        set_vagrant_vars(vagrant_cwd, vagrant_dotfile_path)
    _invoke_vagrant('destroy --force')
    file_delete(get_env_var('TMPDIR_PATH') + '/provider')
    file_delete(get_env_var('TMPDIR_PATH') + '/random_tag')
    dir_delete(os.environ.get('VAGRANT_DOTFILE_PATH'))
    click.echo('Temporary files removed')
    click.echo('Destroy complete.')

def export(resource=None, export_path=None, force=None):
    '''Drop default code in the CWD / user defined space. Operate on saltstack,
    vagrant, or python resources.

    Agrs:
        resource (str): Resource to export: saltstack, vagrant, python, or all.
        export_path (str): Dir to export resources to.
        force (str): Detects if we should overwrite and merge.
    '''
    if export_path:
        output_dir = os.path.normpath(export_path)
    else:
        output_dir = os.getcwd()

    if resource in ('vagrant', 'saltstack'):
        srcs = [os.path.normpath(os.path.join(PROJECT_LOCATION, resource))]
        dsts = [os.path.join(output_dir, resource)]

    if resource == 'vagrant':
        srcs.append(os.path.normpath(os.path.join(PROJECT_LOCATION, 'settings.json')))
        srcs.append(os.path.normpath(os.path.join(PROJECT_LOCATION, 'Vagrantfile')))
        dsts.append(os.path.join(output_dir, 'settings.json'))
        dsts.append(os.path.join(output_dir, 'Vagrantfile'))

    if resource == 'python':
        srcs = [os.path.normpath(os.path.join(PROJECT_LOCATION, 'settings.json'))]
        dsts = [os.path.join(output_dir, 'settings.json')]
        for file in os.listdir(os.path.normpath(os.path.join(PROJECT_LOCATION))):
            if file.endswith('.py'):
                srcs.append(os.path.normpath(os.path.join(PROJECT_LOCATION, file)))
                dsts.append(os.path.join(output_dir, file))

    if resource == 'all':
        srcs = []
        dsts = []
        for file in os.listdir(os.path.normpath(os.path.join(PROJECT_LOCATION))):
            srcs.append(os.path.normpath(os.path.join(PROJECT_LOCATION, file)))
            dsts.append(os.path.join(output_dir, file))

    if not force:
        try:
            for path in dsts:
                if os.path.exists(path):
                    click.confirm("One or more destination files or directories in "
                                  "'%s' already exists. Attempt to merge and "
                                  "overwrite?" % dsts, abort=True)
                    break # We only need general confirmation of an overwrite once.
        except UnboundLocalError: # dsts referenced before assignement
            abort("The resource '%s' is not a valid option." % resource)

    for src, dst in zip(srcs, dsts):
        try:
            distutils.dir_util.copy_tree(src, dst) # Merge copy tree with overwrites.
        except DistutilsFileError: # It's a file, not a dir.
            try:
                shutil.copy(src, dst) # Copy file with overwrites.
            except FileNotFoundError:
                os.makedirs(os.path.dirname(dst), exist_ok=True) # Make parent dirs if needed. # Py 3.2+
                shutil.copy(src, dst) # Copy file with overwrites.

    click.echo('Done exporting %s code.' % resource)

def setup():
    '''Install all default plugins and setup auth directory.
    '''
    install_plugins()

def install_auth(output_path=None):
    '''Install auth directory.
    '''
    if not output_path:
        output_path = get_env_var('cwd')
    license_dir = os.path.join(output_path, 'auth/licenses')
    try:
        os.makedirs(license_dir)
    except FileExistsError:
        pass # Dir already created. Moving on.
    click.echo('Any (license) files you put in %s will be synced into your VM.'
               % license_dir)

    for filename in os.listdir(os.path.join(get_env_var('env'), 'auth/env_scripts')):
        dst_dir = os.path.join(output_path, 'auth/keys')
        dst = os.path.join(dst_dir, os.path.splitext(filename)[0])
        if not os.path.isfile(dst):
            os.makedirs(dst_dir, exist_ok=True) # Make parent dirs if needed. # Py 3.2+
            shutil.copy(os.path.join(get_env_var('env'), 'auth/env_scripts', filename), dst)
            click.echo('Added template key loading scripts %s to auth/keys.' % filename)
        else:
            click.echo('File %s exists. Leaving it.' % dst)

    # TODO: Have Rambo optionally store the same keys that may be in auth/keys in metadata,
    # added from the cli/api. Automatically check if keys in metatdata and not keys
    # in env vars, and set them. This is an avenue for expanding the cli/api's use
    # and not needing the auth key scripts.
    # load_provider_keys()

def install_plugins(force=None, plugins=('all',)):
    '''Install all of the vagrant plugins needed for all plugins
    '''
    for plugin in plugins:
        if plugin == 'all':
            click.echo('Installing all default plugins.')
            for plugin in SETTINGS['PLUGINS']:
                _invoke_vagrant('plugin install %s' % plugin)
        elif plugin in SETTINGS['PLUGINS']:
            _invoke_vagrant('plugin install %s' % plugin)
        else:
            if not force:
                click.confirm('The plugin "%s" is not in our list of plugins. Attempt '
                          'to install anyway?' % plugin, abort=True)
            _invoke_vagrant('plugin install %s' % plugin)

def ssh(ctx=None, vagrant_cwd=None, vagrant_dotfile_path=None):
    '''Connect to an running VM / container over ssh.
    All str args can also be set as an environment variable; arg takes precedence.

    Agrs:
        ctx (object): Click Context object.
        vagrant_cwd (str): Location of `Vagrantfile`.
        vagrant_dotfile_path (str): Location of `.vagrant` metadata directory.
    '''
    # TODO: Better logs.
    if not ctx: # Else handled by cli.
        set_init_vars()
        set_vagrant_vars(vagrant_cwd, vagrant_dotfile_path)

    os.system('vagrant ssh')

def up(ctx=None, provider=None, vagrant_cwd=None, vagrant_dotfile_path=None):
    '''Start a VM / container with `vagrant up`.
    All str args can also be set as an environment variable; arg takes precedence.

    Agrs:
        ctx (object): Click Context object. Used to detect if CLI is used.
        provider (str): Sets provider used.
        vagrant_cwd (str): Location of `Vagrantfile`.
        vagrant_dotfile_path (str): Location of `.vagrant` metadata directory.
    '''
    # TODO: Add registering of VM for all of this installation to see

    if not ctx: # Else handled by cli.
        set_init_vars()
        set_vagrant_vars(vagrant_cwd, vagrant_dotfile_path)

    if provider:
        set_env_var('provider', provider)
        if provider not in PROVIDERS:
            abort('Target provider "%s" is not in the providers '
                  'list. Did you have a typo?' % provider)
    elif get_env_var('PROVIDER') and get_env_var('PROVIDER') not in PROVIDERS:
        abort('Target provider "%s" is set as an environment '
              'variable, and is not in the providers list. Did you '
              'have a typo?' % provider)

    _invoke_vagrant('up')

def vagrant_general_command(cmd):
    '''Invoke vagrant with custom command.

    Args:
        cmd (str): String to append to command `vagrant ...`
    '''
    # Modify cmd in private function to keep enforcement of being a vagrant cmd there.
    _invoke_vagrant(cmd)

## Unused defs
def setup_lastpass():
    dir_create(get_user_home() + '/.tmp-common')
    open(get_user_home() + '/.tmp-common/install-lastpass-log','w')
    dir_create(get_user_home() + '/.tmp-common')
    with open(get_user_home() + '/.tmp-common/install-lastpass.sh', 'w') as file_obj:
        file_obj.write(install_lastpass)
    # Not used, and won't work as is because we're now enforcing use of vagrant in private function.
    _invoke_vagrant('cd ' + get_user_home() + '/.tmp-common; bash install-lastpass.sh', ' install-lastpass-log')


class Run_app():
    def __init__(self):
        print("in Run_app __init__")
