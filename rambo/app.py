import errno
import os
import platform
import pty
import shutil
import sys
from distutils.dir_util import copy_tree
from distutils.errors import DistutilsFileError
from select import select
from subprocess import Popen

import click

import rambo.options as options
import rambo.utils as utils
from rambo.settings import SETTINGS, PROJECT_LOCATION, PROJECT_NAME
from rambo.routing import pure_providers
from rambo.ops.digitalocean import up as pure_up
from rambo.ops.synthetic import up as synthetic_up

from rambo.core import export, set_tmpdir, install_config, install_auth
from rambo.utils import get_env_var, set_env_var

## Defs for cli subcommands
def createproject(project_name, cwd, tmpdir, config_only=None, ctx=None):
    """Create project with basic configuration files.

    Agrs:
        project_name (path): Place to create a new project. Must be non-existing dir.
        config_only (bool): Determins if we should only place a conf file in the new project.
    """
    # initialize paths
    # cwd = set_cwd(cwd)
    # path = os.path.join(cwd, project_name)
    # set_tmpdir(path)
    cwd = "/Users/mike/Desktop"
    path = os.path.join(cwd, project_name)
    set_tmpdir(path)
    pass

class Run_app:
    def __init__(self):
        print("in Run_app __init__")
