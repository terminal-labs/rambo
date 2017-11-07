import os
import sys
import time
import json
from threading import Thread

import click
from bash import bash

from rambo.utils import get_user_home, set_env_var, get_env_var, dir_exists, dir_create, dir_delete, file_delete
from rambo.scripts import install_lastpass

## GLOBALS
# Create env var indicating where this code lives. This will be used latter by
# Vagrant as a check that the python cli is being used, as well as being a useful var.
PROJECT_LOCATION = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(PROJECT_LOCATION, 'settings.json'), 'r') as f:
    SETTINGS = json.load(f)
PROVIDERS = SETTINGS['PROVIDERS']
PROJECT_NAME = SETTINGS['PROJECT_NAME']

# XXX: We should refactor this to catch output directly from Vagrant, and pass it to
# the shell and a copy to log file. Doing logic on the contents of a log file isn't going to be
# stable. For instance, we shouldn't have to specify any exit_triggers. We can't factor in every
# kind of exit_trigger Vagrant can produce. Refactoring will also allow for more control over
# the log file because we're the only ones writing to it. We'll be able to keep old logs,
# append, cycle file names, etc
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

def set_init_vars():
    '''Set custom environment variables that are always going to be needed by
    our custom Ruby code in the Vagrantfile chain.
    '''
    # env vars available to Python and Ruby
    set_env_var('ENV', PROJECT_LOCATION) # location of this code
    set_env_var('TMP', os.path.join(os.getcwd(), '.' + PROJECT_NAME + '-tmp')) # tmp in cwd

def set_vagrant_vars(vagrant_cwd=None, vagrant_dotfile_path=None):
    '''Set the environment varialbes prefixed with `VAGRANT_` that vagrant
    expects, and that we use, to modify some use paths.

    Agrs:
        vagrant_cwd (str): Location of `Vagrantfile`.
        vagrant_dotfile_path (str): Location of `.vagrant` metadata directory.
    '''

    if vagrant_cwd: # loc of Vagrantfile
        os.environ["VAGRANT_CWD"] = vagrant_cwd # custom
    elif 'VAGRANT_CWD' not in os.environ:
        os.environ['VAGRANT_CWD'] = PROJECT_LOCATION # (default installed path)

    if vagrant_dotfile_path: # loc of .vagrant dir
        os.environ['VAGRANT_DOTFILE_PATH'] = vagrant_dotfile_path # custom
    elif 'VAGRANT_DOTFILE_PATH' not in os.environ:
        os.environ['VAGRANT_DOTFILE_PATH'] = os.path.normpath(os.path.join(os.getcwd() + '/.vagrant')) # (default cwd)

def vagrant_up_thread():
    '''Make the final call over the shell to `vagrant up`, and redirect
    all output to log file.
    '''

    dir_create(get_env_var('TMP') + '/logs')
    # TODO: Better logs.
    bash('vagrant up >' + get_env_var('TMP') + '/logs/vagrant-up-log 2>&1')

def vagrant_up(ctx=None, provider=None, vagrant_cwd=None, vagrant_dotfile_path=None):
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

    if not dir_exists(get_env_var('TMP')):
        dir_create(get_env_var('TMP'))
    dir_create(get_env_var('TMP') + '/logs')
    # TODO: Better logs.
    open(get_env_var('TMP') + '/logs/vagrant-up-log','w').close() # Create log file. Vagrant will write to it, we'll read it.

    thread = Thread(target = vagrant_up_thread) # Threaded to write, read, and echo as `up` progresses.
    thread.start()
    follow_log_file(get_env_var('TMP') + '/logs/vagrant-up-log', ['Total run time:',
                                                 'Provisioners marked to run always will still run',
                                                 'Print this help',
                                                 'try again.'])
    click.echo('Up complete.')

def vagrant_ssh(ctx=None, vagrant_cwd=None, vagrant_dotfile_path=None):
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

def vagrant_destroy(ctx=None, vagrant_cwd=None, vagrant_dotfile_path=None):
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


    dir_create(get_env_var('TMP') + '/logs')
    # TODO: Better logs.
    bash('vagrant destroy --force >' + get_env_var('TMP') + '/logs/vagrant-destroy-log 2>&1')
    follow_log_file( get_env_var('TMP') + '/logs/vagrant-destroy-log', ['Vagrant done with destroy.',
                                                      'Print this help'])
    file_delete(get_env_var('TMP') + '/provider')
    file_delete(get_env_var('TMP') + '/random_tag')
    dir_delete(os.environ.get('VAGRANT_DOTFILE_PATH'))
    click.echo('Temporary files removed')
    click.echo('Destroy complete.')

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
