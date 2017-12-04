import os
import sys
import time
import json
import shutil
import distutils
import subprocess
from distutils.dir_util import copy_tree
from distutils.errors import DistutilsFileError
from threading import Thread

import click
from bash import bash

from rambo.providers import load_provider_keys
from rambo.scripts import install_lastpass
from rambo.utils import get_user_home, set_env_var, get_env_var, dir_exists, dir_create, dir_delete, file_delete


## GLOBALS
# Create env var indicating where this code lives. This will be used latter by
# Vagrant as a check that the python cli is being used, as well as being a useful var.
PROJECT_LOCATION = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(PROJECT_LOCATION, 'settings.json'), 'r') as f:
    SETTINGS = json.load(f)
PROVIDERS = SETTINGS['PROVIDERS']
PROJECT_NAME = SETTINGS['PROJECT_NAME']

## XXX: We should refactor this to catch output directly from Vagrant, and pass it to
## the shell and a copy to log file. Doing logic on the contents of a log file isn't going to be
## stable. For instance, we shouldn't have to specify any exit_triggers. We can't factor in every
## kind of exit_trigger Vagrant can produce. Refactoring will also allow for more control over
## the log file because we're the only ones writing to it. We'll be able to keep old logs,
## append, cycle file names, etc.
##
## Once this is done both the follow_log_file and run_cmd can probably be removed.
def follow_log_file(log_file_path, exit_triggers):
    '''Read a file as it's being written and direct each line to stdout.

    Args:
        log_file_path (str): Location of the file to be read.
        exit_triggers (str): String to look for in the file that tells us to
                             stop reading it.
    '''
    file_obj = open(log_file_path, 'r')
    while 1:
        where = file_obj.tell()
        line = file_obj.readline()
        if not line:
            time.sleep(0.1)
            file_obj.seek(where)
        else:
            click.echo(line.strip()) # Strip trailing eol. Echo before break.
            if any(string in line for string in exit_triggers):
                break

def run_cmd(cmd):
    '''Run a cmd in the shell, and output stdout and stderr.
    This blocks until completion and then outputs both buffers once the
    process is completed. This does no logging.
    '''
    if isinstance(cmd, str):
        cmd = cmd.split()

    sp = subprocess.Popen(
        cmd,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE)
    out, err = sp.communicate()
    click.echo(out)
    click.echo(err, err=True)

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
            click.echo('Your current working directory no longer exists. '
                       'Did you delete it? Check for it with `ls ..`', err=True)
            raise click.Abort()

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

    dir_create(get_env_var('TMPDIR_PATH') + '/logs')
    # TODO: Better logs.
    bash('vagrant destroy --force >' + get_env_var('TMPDIR_PATH') + '/logs/vagrant-destroy-log 2>&1')
    follow_log_file(get_env_var('TMPDIR_PATH') + '/logs/vagrant-destroy-log',
                    ['Vagrant done with destroy.',
                     'Print this help'])
    file_delete(get_env_var('TMPDIR_PATH') + '/provider')
    file_delete(get_env_var('TMPDIR_PATH') + '/random_tag')
    dir_delete(os.environ.get('VAGRANT_DOTFILE_PATH'))
    click.echo('Temporary files removed')
    click.echo('Destroy complete.')

def export(force=None, resource=None, export_path=None):
    '''Drop default code in the CWD / user defined space. Operate on saltstack,
    vagrant, or python resources.

    Agrs:
        force (str): Detects if we should overwrite and merge.
        resource (str): Resource to export: saltstack, vagrant, python, or all.
        export_path (str): Dir to export resources to.
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
        for path in dsts:
            if os.path.exists(path):
                click.confirm("One or more destination files or directories in "
                              "'%s' already exists. Attempt to merge and "
                              "overwrite?" % dsts, abort=True)
                break # We only need general confirmation of an overwrite once.

    for src, dst in zip(srcs, dsts):
        try:
            distutils.dir_util.copy_tree(src, dst) # Merge copy tree with overwrites.
        except DistutilsFileError: # It's a file, not a dir.
            try:
                shutil.copy(src, dst) # Copy file with overwrites.
            except FileNotFoundError:
                os.makedirs(os.path.dirname(dst), exist_ok=True) # Make parent dirs if needed.
                shutil.copy(src, dst) # Copy file with overwrites.

    click.echo('Done exporting %s code.' % resource)

def init():
    '''Install all default plugins and setup auth directory.
    '''
    install_auth()
    install_plugins()

def install_auth():
    '''Install auth directory.
    '''
    license_dir = os.path.join(get_env_var('cwd'), 'auth/licenses')
    try:
        os.makedirs(license_dir)
        click.echo('The path %s was just created.'
                   % license_dir)
    except FileExistsError:
        pass # Dir already created. Moving on.
    click.echo('Any (license) files you put in %s will be synced into your VM.'
               % license_dir)

    for filename in os.listdir(os.path.join(get_env_var('env'), 'auth/env_scripts')):
        dst = os.path.join(get_env_var('cwd'), 'auth/keys', os.path.splitext(filename)[0])
        if not os.path.isfile(dst):
            shutil.copy(os.path.join(get_env_var('env'), 'auth/env_scripts', filename), dst)
            click.echo('Added template key loading scripts to %s.' % dst)
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
                run_cmd('vagrant plugin install %s' % plugin)
        elif plugin in SETTINGS['PLUGINS']:
            run_cmd('vagrant plugin install %s' % plugin)
        else:
            if not force:
                click.confirm('The plugin "%s" is not in our list of plugins. Attempt '
                          'to install anyway?' % plugin, abort=True)
            run_cmd('vagrant plugin install %s' % plugin)

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

def up_thread():
    '''Make the final call over the shell to `vagrant up`, and redirect
    all output to log file.
    '''
    # TODO: Better logs.
    bash('vagrant up >' + get_env_var('TMPDIR_PATH') + '/logs/vagrant-up-log 2>&1')

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

    # Point to custom saltstack dir if we have it.
    if 'saltstack' in os.listdir(get_env_var('cwd')):
        set_env_var('salt_dir', get_env_var('cwd'))
    else:
        set_env_var('salt_dir', PROJECT_LOCATION)

    # TODO See if there's a better exit / error system
    if provider:
        set_env_var('provider', provider)
        if provider not in PROVIDERS:
            sys.exit('ABORTED - Target provider "%s" is not in the providers '
                     'list. Did you have a typo?' % provider)
    elif get_env_var('PROVIDER') and get_env_var('PROVIDER') not in PROVIDERS:
        sys.exit('ABORTED - Target provider "%s" is set as an environment '
                 ' variable, and is not in the providers list. Did you '
                 'have a typo?' % provider)

    if not dir_exists(get_env_var('TMPDIR_PATH')):
        dir_create(get_env_var('TMPDIR_PATH'))
    dir_create(get_env_var('TMPDIR_PATH') + '/logs')    # TODO: Better logs.
    open(get_env_var('TMPDIR_PATH') + '/logs/vagrant-up-log','w').close() # Create log file. Vagrant will write to it, we'll read it.

    thread = Thread(target = up_thread) # Threaded to write, read, and echo as `up` progresses.
    thread.start()
    follow_log_file(get_env_var('TMPDIR_PATH') + '/logs/vagrant-up-log',
                    ['Total run time:',
                     'Provisioners marked to run always will still run',
                     'Print this help',
                     'try again.',
                     'Local data directory: /.vagrant',
    ])
    click.echo('Up complete.')

## Unused defs
def setup_lastpass_thread(vagrant_cwd=None, vagrant_dotfile_path=None):
    dir_create(get_user_home() + '/.tmp-common')
    with open(get_user_home() + '/.tmp-common/install-lastpass.sh', 'w') as file_obj:
        file_obj.write(install_lastpass)
    bash('cd ' + get_user_home() + '/.tmp-common; bash install-lastpass.sh > install-lastpass-log')
    with open(get_user_home() + '/.tmp-common/install-lastpass-log', 'a') as file_obj:
        file_obj.write('done installing lastpass')

def setup_lastpass():
    dir_create(get_user_home() + '/.tmp-common')
    open(get_user_home() + '/.tmp-common/install-lastpass-log','w')
    thread = Thread(target = setup_lastpass_thread)
    thread.start()
    follow_log_file(get_user_home() + '/.tmp-common/install-lastpass-log', ['one installing lastpass'])


class Run_app():
    def __init__(self):
        print("in run app init")
