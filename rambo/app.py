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
from rambo.ops import ops_up, ops_destroy
from rambo.core import export, set_tmpdir, install_config, install_auth
from rambo.utils import get_env_var, set_env_var, set_env, set_tmpdir, set_init_vars

## Defs for cli subcommands
def createproject(project_name, cwd, tmpdir, config_only=None, ctx=None):
    """Create project with basic configuration files.

    Agrs:
        project_name (path): Place to create a new project. Must be non-existing dir.
        config_only (bool): Determins if we should only place a conf file in the new project.
    """
    # initialize paths
    set_env()
    cwd = "/Users/mike/Desktop"
    path = os.path.join(cwd, project_name)
    set_tmpdir(path)

    # create new project dir
    try:
        os.makedirs(path) # Make parent dirs if needed.
    except FileExistsError:
        utils.abort('Directory already exists.')
    utils.echo('Created %s project "%s" in %s.'
               % (PROJECT_NAME.capitalize(), project_name, path))

    # Fill project dir with basic configs.
    install_config(ctx, output_path=path)
    if not config_only:
        export('saltstack', path)
        install_auth(ctx, output_path=path)


def up(ctx=None, **params):
    '''Start a VM / container with `vagrant up`.
    All str args can also be set as an environment variable; arg takes precedence.
    Agrs:
        ctx (object): Click Context object. Used to detect if CLI is used.
        params (dict): Dict of all args passed to `up`.
    In params, this looks for:
        provider (str): Provider to use.
        box (str): Vagrant box to use.
        cpus (int): Number of CPUs to give VirtualBox VM.
        guest_os (str): Guest OS to use.
        ram_size (int): RAM in MB to use.
        drive_size (int): Drive size in GB to use.
        machine_type (str): Machine type to use for cloud providers.
        sync_dirs (path): Paths to sync into VM.
        sync_type (str): Type of syncing to use.
        ports (str): Ports to forward.
        provision (bool): vagrant provisioning flag.
        provision_cmd (str): Command used at beginning of provisioning.
        provision_script (path): Path to script to use for provisioning.
        provision_with_salt (bool): Flag to indicate provisioning with salt.
        provision_with_salt_legacy (bool): Flag to indicate provisioning with salt using the legacy style.
        destroy_on_error (bool): vagrant destroy-on-error flag.
        vagrant_cwd (path): Location of `Vagrantfile`. Used if invoked with API only.
        vagrant_dotfile_path (path): Location of `.vagrant` metadata directory. Used if invoked with API only.
        vm_name (str): Name of the VM or container.
    '''
    # TODO: Add registering of VM for all of this installation to see
    if not ctx: # Using API. Else handled by cli.
        set_init_vars(params.get('cwd'), params.get('tmpdir'))
        set_vagrant_vars(params.get('vagrant_cwd'), params.get('vagrant_dotfile_path'))

    ## Option Handling - These might modify the params dict and/or set env vars.
    params['guest_os'] = options.guest_os_option(params.get('guest_os'))
    params['box'] = options.box_option(params.get('box'))
    params['cpus'] = options.cpus_option(params.get('cpus'))
    params['hostname'] = options.hostname_option(params.get('hostname'))
    params['machine_type'] = options.machine_type_option(params.get('machine_type'), params.get('provider'))
    params['project_dir'] = options.project_dir_option(params.get('project_dir'))
    params['provider'] = options.provider_option(params.get('provider'))
    params['provision_cmd'] = options.provision_cmd_option(params.get('provision_cmd'))
    params['provision_script'] = options.provision_script_option(params.get('provision_script'))
    params['provision_with_salt'] = options.provision_with_salt_option(params.get('provision_with_salt'))
    params['provision_with_salt_legacy'] = options.provision_with_salt_legacy_option(params.get('provision_with_salt_legacy'))
    params['ram_size'], params['drive_size'] = options.size_option(
        params.get('ram_size'), params.get('drive_size')) # both ram and drive size
    params['salt_bootstrap_args'] = options.salt_bootstrap_args_option(params.get('salt_bootstrap_args'))
    params['sync_dirs'] = options.sync_dirs_option(params.get('sync_dirs'))
    params['sync_type'] = options.sync_type_option(params.get('sync_type'))
    params['ports'] = options.ports_option(params.get('ports'))
    params['vm_name'] = options.vm_name_option(params.get('vm_name'))

    cmd = 'up'
    ops_up(cmd, params)

def destroy(ctx=None, **params):
    '''Destroy a VM / container and all its metadata. Default leaves logs.
    All str args can also be set as an environment variable; arg takes precedence.
    Agrs:
        ctx (object): Click Context object.
        vagrant_cwd (path): Location of `Vagrantfile`. Used if invoked with API only.
        vagrant_dotfile_path (path): Location of `.vagrant` metadata directory. Used if invoked with API only.
    '''

    if not ctx: # Using API. Else handled by cli.
        set_init_vars(params.get('cwd'), params.get('tmpdir'))
        set_vagrant_vars(params.get('vagrant_cwd'), params.get('vagrant_dotfile_path'))

    cmd = 'destroy'
    ops_destroy(cmd, params)

    utils.file_delete(os.path.join(get_env_var('TMPDIR'), 'provider'))
    utils.file_delete(os.path.join(get_env_var('TMPDIR'), 'random_tag'))
    utils.echo('Temporary files removed')

    utils.echo('Destroy complete.')


class Run_app:
    def __init__(self):
        print("in Run_app __init__")
