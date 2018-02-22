import json
import os
import sys
from pathlib import Path
from shutil import copyfile, move, rmtree

import click

from rambo.settings import PROJECT_NAME


def set_env_var(name, value):
    '''Set an environment variable in all caps that is prefixed with the name of the project
    '''
    os.environ[PROJECT_NAME.upper() + "_" + name.upper()] = str(value)

def get_env_var(name):
    '''Get an environment variable in all caps that is prefixed with the name of the project
    '''
    return os.environ.get(PROJECT_NAME.upper() + "_" + name.upper())

def abort(message):
    sys.exit(click.style(''.join(['ABORTED - ', message]), fg='red', bold=True))

def warn(message):
    click.secho(''.join(['WARNING - ', message]), fg='yellow')

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
