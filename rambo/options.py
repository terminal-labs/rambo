import ast
import os
from pathlib import Path

import rambo.utils as utils
from rambo.settings import SETTINGS
from rambo.utils import set_env_var

def box_option(box=None):
    '''Set box

    Args:
        box (str): Vagrant box to use.

    Return box (str)
    '''
    if box:
        set_env_var('box', box)
    return box

def cpus_option(cpus=None):
    """Set cpus

    Args:
        cpus (int): CPUs for VirtualBox VM

    Return cpus (int)
    """
    if cpus and 1 <= int(cpus) <= 32:
        set_env_var('cpus', cpus)
        return cpus
    elif cpus:
        utils.warn("CPUs must be an int in [1, 32]. Falling back to 1.")

    set_env_var('cpus', 1)
    return 1



def guest_os_option(guest_os=None):
    '''Validate guest_os. If not supplied, set to default. Set as env var.

    Args:
        guest_os (str): Guest OS to use.

    Return guest_os (str)
    '''
    if not guest_os:
        guest_os = SETTINGS['GUEST_OSES_DEFAULT']
    set_env_var('guest_os', guest_os)

    if guest_os not in SETTINGS['GUEST_OSES']:
        msg = ('Guest OS "%s" is not in the guest OSes whitelist.\n'
               'Did you have a typo? We\'ll try anyway.\n'
               'Here is as list of avalible guest OSes:\n\n'
               % guest_os)
        for supported_os in SETTINGS['GUEST_OSES']:
            msg = msg + '%s\n' % supported_os
        utils.warn(msg)
    return guest_os

def hostname_option(hostname=None):
    """Validate hostname

    Args:
        hostname (str): Hostname to set in VM / container

    Return hostname (str)

    """
    if hostname and len(hostname) > 64:
        utils.warn(
            "Hostnames of many OSes are limited to 64 characters."
            f"The current hostname {hostname} is {len(hostname)}."
        )

    if hostname:
        set_env_var('hostname', hostname)

    return hostname

def machine_type_option(machine_type=None, provider=None):
    '''Validate machine_type. If not supplied, set to default. Set as env var.

    Args:
        machine_type (str): Machine type to use for cloud providers.
        provider (str): Provider to use.

    Return machine_type (str)
    '''
    if machine_type:
        if provider in ('docker', 'lxc', 'virtualbox'):
            msg = ('You have selected a machine-type, but are not using\n'
                   'a cloud provider. You selected %s with %s.\n'
                   % (machine_type, provider))
            utils.abort(msg)
        set_env_var('machinetype', machine_type)
    return machine_type

def ports_option(ports=None):
    '''Validate ports. If not supplied, set to default. Set as env var.

    ports must be list of lists of form:
    `[['guest_port', 'host_port'], ['guest_port2', 'host_port2']]`

    Args:
        ports: Paths to sync into VM, supplied as list of lists.

    Return ports (list)
    '''
    if not ports:
        return None

    try:
        ports = ast.literal_eval(ports)
    except SyntaxError:
        utils.abort("ports cannot be evaluated as valid Python.")
    if type(ports) is not list:
        utils.abort(
            f"`ports` was not evaluated as a Python list, but as '{type(ports)}'."
        )
    for port_pair in ports:
        if type(port_pair) is not list:
            utils.abort(
                f"`ports` element {port_pair} was not evaluated as a Python list, but as "
                f"'{type(port_pair)}'."
            )
        if len(port_pair) != 2:
            utils.abort(f"Not the right number of ports to forward in {port_pair}.")
        for port in port_pair:
            if type(port_pair) != int and not 0 < port < 65535:
                utils.abort(f"{port} in `ports` is not an int in a valid port range.")

    set_env_var('ports', ports)
    return ports

def project_dir_option(project_dir=None):
    '''Validate project_dir. If not supplied, set to default. Set as env var.

    Args:
        project_dir: Path to sync into VM.

    Return project_dir (path)
    '''
    if not project_dir:
        project_dir = os.getcwd()

    set_env_var('project_dir', project_dir)

    return project_dir

def provider_option(provider=None):
    '''Validate provider. If not supplied, set to default. Set as env var.

    Args:
        provider (str): Provider to use.

    Return provider (str)
    '''
    if not provider:
        provider = SETTINGS['PROVIDERS_DEFAULT']
    set_env_var('provider', provider)

    if provider not in SETTINGS['PROVIDERS']:
        msg = ('Provider "%s" is not in the provider list.\n'
           'Did you have a typo? Here is as list of avalible providers:\n\n'
           % provider)
        for supported_provider in SETTINGS['PROVIDERS']:
            msg = msg + '%s\n' % supported_provider
        utils.abort(msg)
    return provider


def command_option(command=None):
    '''Load command into env var.

    Args:
        command (str): Command to run at the begginning of provisioning.

    Return command (str)
    '''
    if command:
        set_env_var('command', command)

    return command


def size_option(ram_size=None, drive_size=None):
    '''Validate ram and drive sizes. Pair them if possible. If not
    supplied, set to default. Set as env var. Reset in params as strings.

    Args:
        ram_size (int): RAM in MB to use.
        drive_size (int): Drive size in GB to use.

    Return (ram_size, drive_size) (tuple, where values are (str, str))
    '''
    # Cast to strings if they exist so they can stored as env vars.
    if ram_size:
        ram_size = str(ram_size)
    if drive_size:
        drive_size = str(drive_size)

    if ram_size and not drive_size:
        try:
            drive_size = SETTINGS['SIZES'][ram_size]
        except KeyError: # Doesn't match, but we'll let them try it.
            drive_size = SETTINGS['DRIVESIZE_DEFAULT']
    elif drive_size and not ram_size:
        try:
            ram_size = SETTINGS['SIZES'][
                list(SETTINGS['SIZES'].values()).index(drive_size)]
        except ValueError: # Doesn't match, but we'll let them try it.
            ram_size = SETTINGS['RAMSIZE_DEFAULT']
    elif not ram_size and not drive_size:
        ram_size = SETTINGS['RAMSIZE_DEFAULT']
        drive_size = SETTINGS['DRIVESIZE_DEFAULT']
    # else both exist, just try using them

    set_env_var('ramsize', ram_size)
    set_env_var('drivesize', drive_size)

    ## ram_size
    if ram_size not in SETTINGS['SIZES']:
        msg = ('RAM Size "%s" is not in the RAM sizes list.\n'
               'Did you have a typo? We\'ll try anyway.\n'
               'Here is as list of avalible RAM sizes:\n\n'
               % ram_size)
        for supported_ram_size in SETTINGS['SIZES']:
            msg = msg + '%s\n' % supported_ram_size
        utils.warn(msg)

    ## drive_size
    if drive_size not in SETTINGS['SIZES'].values():
        msg = ('DRIVE Size "%s" is not in the DRIVE sizes list.\n'
               'Did you have a typo? We\'ll try anyway.\n'
               'Here is as list of avalible DRIVE sizes:\n\n'
               % drive_size)
        for supported_drive_size in SETTINGS['SIZES'].values():
            msg = msg + '%s\n' % supported_drive_size
        utils.warn(msg)
    return (ram_size, drive_size)

def sync_dirs_option(sync_dirs=None):
    '''Validate sync_dirs. If not supplied, set to default. Set as env var.

    sync_dirs must be list of lists of form:
    `"[['guest_dir', 'host_dir'], ['guest_dir2', 'host_dir2']]"`

    Args:
        sync_dirs: Paths to sync into VM, supplied as list of lists.

    Return sync_dirs (list)
    '''
    if not sync_dirs:
        return None

    try:
        sync_dirs = ast.literal_eval(sync_dirs)
    except SyntaxError:
        utils.abort("sync_dirs cannot be evaluated as valid Python.")
    if type(sync_dirs) is not list:
        utils.abort(
            f"sync_dirs was not evaluated as a Python list, but as '{type(sync_dirs)}'"
        )
    for sd in sync_dirs:
        if type(sd) is not list:
            utils.abort(
                f"sync_dirs element {sd} was not evaluated as a Python list, but as "
                f"'{type(sd)}'"
            )

    # Normalize source dirs. Target Dirs must be absolute / handled by Vagrant.
    sync_dirs = [[os.path.realpath(os.path.expanduser(lst[0])), lst[1]] for lst in sync_dirs]
    set_env_var('sync_dirs', sync_dirs)
    return sync_dirs

def sync_type_option(sync_type=None):
    '''Validate and set sync_type.

    Args:
        sync_type: Type of syncing to use.

    Return sync_type (str)
    '''
    if sync_type in SETTINGS["SYNC_TYPES"]:
        set_env_var('sync_type', sync_type)
    elif sync_type:
        utils.warn(
            f"Sync type {sync_type} not in approved list. Using Vagrant's default."
            f"Supported alternate sync types are {SETTINGS['SYNC_TYPES']}."
        )
        sync_type = None

    return sync_type

def vm_name_option(vm_name=None):
    """Set vm_name

    Args:
        vm_name (str): Vm_Name to set in VM / container

    Return vm_name (str)

    """
    if vm_name:
        set_env_var('vm_name', vm_name)
    return vm_name
