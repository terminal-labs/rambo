import distutils
import errno
import os
import platform
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

import rambo.options as options
import rambo.utils as utils
from rambo.settings import SETTINGS, PROJECT_LOCATION, PROJECT_NAME
from rambo.utils import get_env_var, set_env_var

## Defs for cli subcommands
def createproject(project_name, config_only=None):
    '''Create project with basic configuration files.

    Agrs:
        project_name (path): Place to create a new project. Must be non-existing dir.
        config_only (bool): Determins if we should only place a conf file in the new project.
    '''
    ## Create project dir
    path = os.path.join(os.getcwd(), project_name)
    try:
        os.makedirs(path) # Make parent dirs if needed.
    except FileExistsError:
        utils.abort('Directory already exists.')
    utils.echo('Created %s project "%s" in %s.'
               % (PROJECT_NAME.capitalize(), project_name, path))
    ## Fill project dir with basic configs.
    install_config(output_path=path)
    if not config_only:
        export('saltstack', path)
        install_auth(output_path=path)

def destroy(ctx=None, **params):
    print("stub for destroy")

def halt(ctx=None, *args, **params):
    print("stub for halt")

def install_auth(ctx=None, output_path=None, **params):
    print("stub for auth")

def install_config(ctx=None, output_path=None, **params):
    print("stub for install config")

def scp(ctx=None, locations=None, **params):
    print("stub for scp")

def ssh(ctx=None, command=None, **params):
    print("stub for ssh")

def up(ctx=None, **params):
    print("stub for up")

class Run_app():
    def __init__(self):
        print("in Run_app __init__")
