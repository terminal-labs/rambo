import os
import json

from pathlib import Path
from shutil import copyfile, move, rmtree

## GLOBALS
# Create env var indicating where this code lives. This will be used latter by
# Vagrant as a check that the python cli is being used, as well as being a useful var.
PROJECT_LOCATION = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(PROJECT_LOCATION, 'settings.json'), 'r') as f:
    SETTINGS = json.load(f)
PROVIDERS = SETTINGS['PROVIDERS']
PROJECT_NAME = SETTINGS['PROJECT_NAME']

def set_env_var(name, value):
    '''Set an environment variable in all caps that is prefixed with the name of the project
    '''
    os.environ[PROJECT_NAME.upper() + "_" + name.upper()] = value

def get_env_var(name):
    '''Set an environment variable in all caps that is prefixed with the name of the project
    '''
    return os.environ.get(PROJECT_NAME.upper() + "_" + name.upper())

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
