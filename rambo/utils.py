import json
import os
import sys
from pathlib import Path
from shutil import copyfile, move, rmtree

import re
import tempfile
import zipfile
import tarfile
import shutil
import hashlib

import click
import requests

from rambo.settings import PROJECT_NAME

HOME = os.path.expanduser('~')
CWD = os.getcwd()
CHUNK_SIZE=1024*32
RAMBO_HOME_DIR = '.rambo.d'
SLASH_ENCODING = '-VAGRANTSLASH-'
VAGRANT_API_URL = 'https://app.vagrantup.com/api/v1/box/'

mock_var_dict = {}
mock_var_dict["RAMBO_TMPDIR_PATH"] = PROJECT_NAME + "-tmp"
mock_var_dict["RAMBO_LOG_PATH"] = os.path.join(
    mock_var_dict["RAMBO_TMPDIR_PATH"], "logs"
)


#def set_env_var(name, value):
#    """Set an environment variable in all caps that is prefixed with the name of the project
#    """
#    # os.environ[PROJECT_NAME.upper() + "_" + name.upper()] = str(value)
#    mock_var_dict[PROJECT_NAME.upper() + "_" + name.upper()] = str(value)


#def get_env_var(name):
#    """Get an environment variable in all caps that is prefixed with the name of the project
#    """
#    # return os.environ.get(PROJECT_NAME.upper() + "_" + name.upper())
#    mock_var_dict[PROJECT_NAME.upper() + "_" + name.upper()]


def abort(msg):
    msg = click.style("".join(["ABORTED - ", msg]), fg="red", bold=True)
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

    dir_create(os.path.join(mock_var_dict["RAMBO_TMPDIR_PATH"], "logs"))
    fd_path = os.path.join(mock_var_dict["RAMBO_TMPDIR_PATH"], "history.log")
    fd = open(fd_path, "a+")
    fd.write(data)
    fd.close()
    if file_name:
        fd_custom_path = os.path.join(
            mock_var_dict["RAMBO_TMPDIR_PATH"], "".join([file_name, ".log"])
        )
        fd_custom = open(fd_custom_path, "a+")
        fd_custom.write(data)
        fd_custom.close()


def create_rambo_tmp_dir():
    dir_create(os.path.join(CWD, '.' + PROJECT_NAME + '-tmp'))


def write_json_metadata_file(data):
    create_rambo_tmp_dir()
    with open(os.path.join(CWD, '.' + PROJECT_NAME + '-tmp', 'metadata.json'), 'w') as outfile:
        json.dump(data, outfile)


def get_vagrant_box_metadata(tag):
    r = requests.get(VAGRANT_API_URL + tag)
    return json.loads(r.text)


def init():
    directory = HOME + '/' + RAMBO_HOME_DIR
    if not os.path.exists(directory):
        os.makedirs(directory)

    directory = HOME + '/' + RAMBO_HOME_DIR + '/vboxsdk'
    if not os.path.exists(directory):
        os.makedirs(directory)

    directory = HOME + '/' + RAMBO_HOME_DIR + '/boxes'
    if not os.path.exists(directory):
        os.makedirs(directory)

    directory = HOME + '/' + RAMBO_HOME_DIR + '/raw_boxes'
    if not os.path.exists(directory):
        os.makedirs(directory)


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
