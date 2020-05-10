import os
import sys
import site
from pathlib import Path
from shutil import copyfile, move, rmtree

import click

from rambo.settings import PROJECT_NAME, CONF_FILES
from rambo.settings import SETTINGS, PROJECT_LOCATION, PROJECT_NAME, SITEPACKAGESPATH, EGG_NAME



def dir_exists(path):
    return os.path.isdir(path)


def dir_create(path):
    if not os.path.exists(path):
        os.makedirs(path)


def dir_delete(path):
    try:
        rmtree(path)
    except FileNotFoundError:
        pass


def file_delete(path):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


def file_copy(src, dst):
    copyfile(src, dst)


def file_rename(src, dst):
    os.rename(src, dst)


def file_move(src, dst):
    move(src, dst)


def get_user_home():
    return str(Path.home())


def _resolve_payload_path():
    payload_name = "/payload"
    possible_path = SITEPACKAGESPATH + "/" + EGG_NAME + ".egg-link"
    if exists(possible_path):
        egglink_file = open(possible_path, "r")
        link_path = egglink_file.read().split("\n")[0]
        possible_payload_path = link_path + "/" + PROJECT_NAME + payload_name
    else:
        possible_path = SITEPACKAGESPATH + "/" + PROJECT_NAME
        possible_payload_path = possible_path + payload_name
    return possible_payload_path


## Defs used by main cli cmd
def set_cwd(cwd=None):
    """Set cwd environment variable and change the actual cwd to it.

    Args:
        cwd (path): Location of project (conf file, provisioning scripts, etc.).
    """
    pass

def set_init_vars(cwd=None, tmpdir=None):
    """Set env vars that are used throughout Ruby and Python. If Ruby weren't used
    this would be managed very differently, as these are effectively project scoped
    global variables.

    These calls are split into separate functions because on occaision we need to call
    them more carefully than with this function, as in createproject.
    """
    set_env()
    set_cwd(cwd)
    set_tmpdir(tmpdir)


def set_env():
    set_env_var('ENV', PROJECT_LOCATION) # installed location of this code


def set_tmpdir(tmpdir=None):
    '''Set tmpdir and log_path locations. This should defaut to be inside the cwd.
    Args:
        tmpdir (path): Location of project's tmp dir.
    '''
    # loc of tmpdir
    if tmpdir: # cli / api
        set_env_var('TMPDIR',
                    os.path.join(tmpdir, '.%s-tmp' % PROJECT_NAME))
    elif get_env_var('TMPDIR'): # Previously set env var
        set_env_var('TMPDIR',
                    os.path.join(get_env_var('TMPDIR'),
                                 '.%s-tmp' % PROJECT_NAME))
    else: # Not set, set to default loc
        set_env_var('TMPDIR',
                    os.path.join(os.getcwd(),
                                 '.%s-tmp' % PROJECT_NAME)) # default (cwd)

    set_env_var('LOG_PATH', os.path.join(get_env_var('TMPDIR'), 'logs'))

def set_env_var(name, value):
    """Set an environment variable in all caps that is prefixed with the name of the project
    """
    os.environ[PROJECT_NAME.upper() + "_" + name.upper()] = str(value)


def get_env_var(name):
    """Get an environment variable in all caps that is prefixed with the name of the project
    """
    return os.environ.get(PROJECT_NAME.upper() + "_" + name.upper())


def abort(msg, log=True):
    msg = click.style("".join(["ABORTED - ", msg]), fg="red", bold=True)
    if log:
        write_to_log(msg, "stderr")
    sys.exit(msg)


def echo(msg, err=None):
    if err:
        write_to_log(msg, "stderr")
        click.echo(msg, err=err)
    else:
        write_to_log(msg)
        click.echo(msg)


def warn(msg):
    msg = click.style("".join(["WARNING - ", msg]), fg="yellow")
    echo(msg)


def find_conf(path):
    if any(cf in os.listdir(path) for cf in CONF_FILES):
        return path
    for parent in Path(path).parents:
        if any(cf in os.listdir(parent) for cf in CONF_FILES):
            return parent


def write_to_log(data=None, file_name=None):
    """Write data to log files. Will append data to a single combined log.
    Additionally write data to a log with a custom name (such as stderr)
    for any custom logs.

    Args:
        data (str or bytes): Data to write to log file.
        file_name (str): Used to create (or append to) an additional
                         log file with a custom name. Custom name always gets
                         `.log` added to the end.
    """
    try:
        data = data.decode("utf-8")
    except AttributeError:
        pass  # already a string

    # strip possible eol chars and add back exactly one
    data = "".join([data.rstrip(), "\n"])

    dir_create(get_env_var("LOG_PATH"))
    fd_path = os.path.join(get_env_var("LOG_PATH"), "history.log")
    fd = open(fd_path, "a+")
    fd.write(data)
    fd.close()
    if file_name:
        fd_custom_path = os.path.join(get_env_var("LOG_PATH"), "".join([file_name, ".log"]))
        fd_custom = open(fd_custom_path, "a+")
        fd_custom.write(data)
        fd_custom.close()
