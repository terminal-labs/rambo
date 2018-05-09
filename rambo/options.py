import os

import rambo.utils as utils
from rambo.settings import SETTINGS, PROJECT_LOCATION, PROJECT_NAME


def guest_os_option(guest_os=None):
    """Validate guest_os. If not supplied, set to default. Set as env var.

    Args:
        guest_os (str): Guest OS to use.

    Return guest_os (str)
    """
    if not guest_os:
        guest_os = SETTINGS["GUEST_OSES_DEFAULT"]
    # set_env_var("guest_os", guest_os)

    if guest_os not in SETTINGS["GUEST_OSES"]:
        msg = (
            'Guest OS "%s" is not in the guest OSes whitelist.\n'
            "Did you have a typo? We'll try anyway.\n"
            "Here is as list of avalible guest OSes:\n\n" % guest_os
        )
        for supported_os in SETTINGS["GUEST_OSES"]:
            msg = msg + "%s\n" % supported_os
        utils.warn(msg)
    return guest_os


def machine_type_option(machine_type=None, provider=None):
    """Validate machine_type. If not supplied, set to default. Set as env var.

    Args:
        machine_type (str): Machine type to use for cloud providers.
        provider (str): Provider to use.

    Return machine_type (str)
    """
    if machine_type:
        if provider in ("docker", "lxc", "virtualbox"):
            msg = (
                "You have selected a machine-type, but are not using\n"
                "a cloud provider. You selected %s with %s.\n"
                % (machine_type, provider)
            )
            utils.abort(msg)
        # set_env_var("machinetype", machine_type)
    return machine_type


def provider_option(provider=None):
    """Validate provider. If not supplied, set to default. Set as env var.

    Args:
        provider (str): Provider to use.

    Return provider (str)
    """
    if not provider:
        provider = SETTINGS["PROVIDERS_DEFAULT"]
    # set_env_var("provider", provider)

    if provider not in SETTINGS["PROVIDERS"]:
        msg = (
            'Provider "%s" is not in the provider list.\n'
            "Did you have a typo? Here is as list of avalible providers:\n\n" % provider
        )
        for supported_provider in SETTINGS["PROVIDERS"]:
            msg = msg + "%s\n" % supported_provider
        utils.abort(msg)
    return provider


def size_option(ram_size=None, drive_size=None):
    """Validate ram and drive sizes. Pair them if possible. If not
    supplied, set to default. Set as env var. Reset in params as strings.

    Args:
        ram_size (int): RAM in MB to use.
        drive_size (int): Drive size in GB to use.

    Return (ram_size, drive_size) (tuple, where values are (str, str))
    """
    # Cast to strings if they exist so they can stored as env vars.
    if ram_size:
        ram_size = str(ram_size)
    if drive_size:
        drive_size = str(drive_size)

    if ram_size and not drive_size:
        try:
            drive_size = SETTINGS["SIZES"][ram_size]
        except KeyError:  # Doesn't match, but we'll let them try it.
            drive_size = SETTINGS["DRIVESIZE_DEFAULT"]
    elif drive_size and not ram_size:
        try:
            ram_size = list(SETTINGS["SIZES"].keys())[
                list(SETTINGS["SIZES"].values()).index(drive_size)
            ]
        except ValueError:  # Doesn't match, but we'll let them try it.
            ram_size = SETTINGS["RAMSIZE_DEFAULT"]
    elif not ram_size and not drive_size:
        ram_size = SETTINGS["RAMSIZE_DEFAULT"]
        drive_size = SETTINGS["DRIVESIZE_DEFAULT"]
    # else both exist, just try using them

    # set_env_var("ramsize", ram_size)
    # set_env_var("drivesize", drive_size)

    ## ram_size
    if ram_size not in iter(SETTINGS["SIZES"]):
        msg = (
            'RAM Size "%s" is not in the RAM sizes list.\n'
            "Did you have a typo? We'll try anyway.\n"
            "Here is as list of avalible RAM sizes:\n\n" % ram_size
        )
        for supported_ram_size in iter(SETTINGS["SIZES"]):
            msg = msg + "%s\n" % supported_ram_size
        utils.warn(msg)

    ## drive_size
    if drive_size not in iter(SETTINGS["SIZES"].values()):
        msg = (
            'DRIVE Size "%s" is not in the DRIVE sizes list.\n'
            "Did you have a typo? We'll try anyway.\n"
            "Here is as list of avalible DRIVE sizes:\n\n" % drive_size
        )
        for supported_drive_size in iter(SETTINGS["SIZES"].values()):
            msg = msg + "%s\n" % supported_drive_size
        utils.warn(msg)
    return (ram_size, drive_size)


def sync_dir_option(sync_dir=None):
    """Validate sync_dir. If not supplied, set to default. Set as env var.

    Args:
        sync_dir: Path to sync into VM.

    Return sync_dir (path)
    """
    if not sync_dir:
        sync_dir = os.getcwd()

    set_env_var("sync_dir", sync_dir)

    return sync_dir
