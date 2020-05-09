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
import rambo.vagrant_providers as vagrant_providers
from rambo.settings import SETTINGS, PROJECT_LOCATION, PROJECT_NAME
from rambo.routing import pure_providers
from rambo.pure_ops import pure_up, pure_halt
from rambo.vagrant_ops import _invoke_vagrant, vagrant_general_command, install_plugins, set_vagrant_vars, set_init_vars, set_env, set_cwd, set_tmpdir, vagrant_up, vagrant_halt
from rambo.utils import get_env_var, set_env_var

def export(resource=None, export_path=None, force=None):
    """Drop default code in the CWD / user defined space. Operate on saltstack
    and vagrant resources.

    Agrs:
        resource (str): Resource to export: saltstack or vagrant.
        export_path (path): Dir to export resources to.
        force (bool): Determins if we should overwrite and merge conflicting files in the target path.
    """
    if export_path:
        output_dir = os.path.normpath(export_path)
    else:
        output_dir = os.getcwd()

    if resource in ("vagrant", "saltstack"):
        srcs = [os.path.normpath(os.path.join(PROJECT_LOCATION, resource))]
        dsts = [os.path.join(output_dir, resource)]

    if resource == "vagrant":
        srcs.append(os.path.normpath(os.path.join(PROJECT_LOCATION, "settings.json")))
        srcs.append(os.path.normpath(os.path.join(PROJECT_LOCATION, "Vagrantfile")))
        dsts.append(os.path.join(output_dir, "settings.json"))
        dsts.append(os.path.join(output_dir, "Vagrantfile"))

    if not force:
        try:
            for path in dsts:
                if os.path.exists(path):
                    click.confirm(
                        "One or more destination files or directories in " "'%s' already exists. Attempt to merge and " "overwrite?" % dsts,
                        abort=True,
                    )
                    break  # We only need general confirmation of an overwrite once.
        except UnboundLocalError:  # dsts referenced before assignement
            utils.abort("The resource '%s' is not a valid option." % resource)

    for src, dst in zip(srcs, dsts):
        try:
            copy_tree(src, dst)  # Merge copy tree with overwrites.
        except DistutilsFileError:  # It's a file, not a dir.
            try:
                shutil.copy(src, dst)  # Copy file with overwrites.
            except FileNotFoundError:
                os.makedirs(os.path.dirname(dst), exist_ok=True)  # Make parent dirs if needed. # Py 3.2+
                shutil.copy(src, dst)  # Copy file with overwrites.

    utils.echo("Done exporting %s code." % resource)
