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
from rambo.utils import get_env_var, set_env_var

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
    pass


## Defs used by main cli cmd
def set_cwd(cwd=None):
    """Set cwd environment variable and change the actual cwd to it.

    Args:
        cwd (path): Location of project (conf file, provisioning scripts, etc.).
    """
    pass


def set_tmpdir(tmpdir=None):
    """Set tmpdir and log_path locations. This should defaut to be inside the cwd.

    Args:
        tmpdir (path): Location of project's tmp dir.
    """
    pass

def install_auth(ctx=None, output_path=None, **kwargs):
    """Install auth directory.

    Agrs:
        ctx (object): Click Context object.
        output_path (path): Path to place auth dir.
    """
    pass



def install_config(ctx=None, output_path=None, **kwargs):
    """Install config file.

    Agrs:
        ctx (object): Click Context object.
        output_path (path): Path to place conf file.
    """
    pass


def export(resource=None, export_path=None, force=None):
    """Drop default code in the CWD / user defined space. Operate on saltstack
    and vagrant resources.
    Agrs:
        resource (str): Resource to export: saltstack or vagrant.
        export_path (path): Dir to export resources to.
        force (bool): Determins if we should overwrite and merge conflicting files in the target path.
    """
    pass
