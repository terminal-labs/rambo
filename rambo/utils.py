import os
import sys
from pathlib import Path
from shutil import copyfile
from shutil import move
from shutil import rmtree

import click

from rambo.settings import CONF_FILES
from rambo.settings import PROJECT_NAME


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
        fd_custom_path = os.path.join(
            get_env_var("LOG_PATH"), "".join([file_name, ".log"])
        )
        fd_custom = open(fd_custom_path, "a+")
        fd_custom.write(data)
        fd_custom.close()


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
