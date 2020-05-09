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
from rambo.core import export
from rambo.utils import get_env_var, set_env_var


## Defs for cli subcommands
def createproject(project_name, cwd, tmpdir, config_only=None, ctx=None):
    """Create project with basic configuration files.

    Agrs:
        project_name (path): Place to create a new project. Must be non-existing dir.
        config_only (bool): Determins if we should only place a conf file in the new project.
    """
    # initialize paths
    set_env()
    cwd = set_cwd(cwd)
    path = os.path.join(cwd, project_name)
    set_tmpdir(path)

    # create new project dir
    try:
        os.makedirs(path)  # Make parent dirs if needed.
    except FileExistsError:
        utils.abort("Directory already exists.")
    utils.echo('Created %s project "%s" in %s.' % (PROJECT_NAME.capitalize(), project_name, path))

    # Fill project dir with basic configs.
    install_config(ctx, output_path=path)
    if not config_only:
        export("saltstack", path)
        install_auth(ctx, output_path=path)


def destroy(ctx=None, **params):
    """Destroy a VM / container and all its metadata. Default leaves logs.
    All str args can also be set as an environment variable; arg takes precedence.

    Agrs:
        ctx (object): Click Context object.
        vagrant_cwd (path): Location of `Vagrantfile`. Used if invoked with API only.
        vagrant_dotfile_path (path): Location of `.vagrant` metadata directory. Used if invoked with API only.
    """
    # TODO add finding and deleting of all VMs registered to this installation.
    # TODO (optional) add finding and deleting of all VMs across all installations.
    # TODO add an --all flag to delete the whole .rambo-tmp dir. Default leaves logs.

    if not ctx:  # Using API. Else handled by cli.
        set_init_vars(params.get("cwd"), params.get("tmpdir"))
        set_vagrant_vars(params.get("vagrant_cwd"), params.get("vagrant_dotfile_path"))

    destroy_cmd = vagrant_general_command("destroy --force")

    # If there's any error code from Vagrant, don't delete the metadata.
    if not destroy_cmd:  # I.e. we succeeded - ret code == 0
        utils.file_delete(os.path.join(get_env_var("TMPDIR"), "provider"))
        utils.file_delete(os.path.join(get_env_var("TMPDIR"), "random_tag"))
        utils.dir_delete(os.environ.get("VAGRANT_DOTFILE_PATH"))
        utils.echo("Temporary files removed")

        if params.get("vm_name"):  # Additionally remove the box if we can.
            utils.echo(f"Now removing base VirtualBox data for VM {params['vm_name']}.")
            os.system(f"vboxmanage controlvm {params['vm_name']} poweroff")
            os.system(f"vboxmanage unregistervm {params['vm_name']} --delete")

        utils.echo("Destroy complete.")
    else:
        utils.echo("We received an error. Destroy may not be complete.")


def halt(ctx=None, *args, **params):
    provider = "synthetic"
    if provider not in pure_providers:
        print(provider)
        vagrant_halt(ctx, args, params)
    else:
        print(provider)
        pure_halt(ctx, args, params)


def install_auth(ctx=None, output_path=None, **kwargs):
    """Install auth directory.

    Agrs:
        ctx (object): Click Context object.
        output_path (path): Path to place auth dir.
    """
    if not ctx:  # Using API. Else handled by cli.
        set_init_vars(params.get("cwd"), params.get("tmpdir"))

    if not output_path:
        output_path = get_env_var("cwd")
    license_dir = os.path.join(output_path, "auth/licenses")
    try:
        os.makedirs(license_dir)
    except FileExistsError:
        pass  # Dir already created. Moving on.
    utils.echo("Any (license) files you put in %s will be synced into your VM." % license_dir)

    for filename in os.listdir(os.path.join(get_env_var("env"), "auth/env_scripts")):
        dst_dir = os.path.join(output_path, "auth/keys")
        dst = os.path.join(dst_dir, os.path.splitext(filename)[0])
        if not os.path.isfile(dst):
            os.makedirs(dst_dir, exist_ok=True)  # Make parent dirs if needed. # Py 3.2+
            shutil.copy(os.path.join(get_env_var("env"), "auth/env_scripts", filename), dst)
            utils.echo("Added template key loading scripts %s to auth/keys." % filename)
        else:
            utils.echo("File %s exists. Leaving it." % dst)

    # TODO: Have Rambo optionally store the same keys that may be in auth/keys in metadata,
    # added from the cli/api. Automatically check if keys in metatdata and not keys
    # in env vars, and set them. This is an avenue for expanding the cli/api's use
    # and not needing the auth key scripts.
    # load_provider_keys()


def install_config(ctx=None, output_path=None, **kwargs):
    """Install config file.

    Agrs:
        ctx (object): Click Context object.
        output_path (path): Path to place conf file.
    """
    if not ctx:  # Using API. Else handled by cli.
        set_init_vars(params.get("cwd"), params.get("tmpdir"))

    if not output_path:
        output_path = get_env_var("cwd")
    path = os.path.join(output_path, "%s.conf" % PROJECT_NAME)

    if os.path.exists(path):
        utils.abort("%s.conf already esists." % PROJECT_NAME)
    else:
        with open(path, "w") as f:
            f.write("[up]\nprovider = %s\nguest_os = %s\n" % (SETTINGS["PROVIDERS_DEFAULT"], SETTINGS["GUEST_OSES_DEFAULT"]))
        utils.echo("Created config at %s" % path)


def scp(ctx=None, locations=None, **params):
    """Transfer file or dir with scp. This makes use of the vagrant-scp plugin,
    which allows for simplified args.
    """
    if not ctx:  # Using API. Else handled by cli.
        set_init_vars(params.get("cwd"), params.get("tmpdir"))
        set_vagrant_vars(params.get("vagrant_cwd"), params.get("vagrant_dotfile_path"))

    if len(locations) != 2:
        utils.abort("There needs to be exactly two arguments for scp, a 'from' location " "and a 'to' location.\nYou gave: %s." % " ".join(locations))

    copy_from = locations[0]
    copy_to = locations[1]

    if ":" in copy_from:  # copy_from is remote, fix copy_to which is local
        copy_to = os.path.abspath(copy_to)
    else:  # if no ':' in copy_from, copy_to must be remote, fix copy_from which is local
        copy_from = os.path.abspath(copy_from)

    locations = [copy_from, copy_to]

    vagrant_general_command("{} {}".format("scp", " ".join(locations)))


def ssh(ctx=None, command=None, **params):
    """Connect to an running VM / container over ssh.
    All str args can also be set as an environment variable; arg takes precedence.

    Agrs:
        ctx (object): Click Context object.
        command (str): Pass-through command to run with `vagrant ssh --command`.
        vagrant_cwd (path): Location of `Vagrantfile`. Used if invoked with API only.
        vagrant_dotfile_path (path): Location of `.vagrant` metadata directory. Used if invoked with API only.
    """
    if not ctx:  # Using API. Else handled by cli.
        set_init_vars(params.get("cwd"), params.get("tmpdir"))
        set_vagrant_vars(params.get("vagrant_cwd"), params.get("vagrant_dotfile_path"))

    ## Add pass-through 'command' option.
    cmd = "vagrant ssh"
    if command:
        cmd = " ".join([cmd, "--command", command])

    # do not use _invoke_vagrant, that will give a persistent ssh session regardless.
    os.system(cmd)


def up(ctx=None, **params):
    """Start a VM / container with `vagrant up`.
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
    """

    # pre-routing
    provider = options.provider_option(params.get("provider"))
    if provider not in pure_providers:
        # TODO: Add registering of VM for all of this installation to see
        if not ctx:  # Using API. Else handled by cli.
            set_init_vars(params.get("cwd"), params.get("tmpdir"))
            set_vagrant_vars(params.get("vagrant_cwd"), params.get("vagrant_dotfile_path"))
    else:
        print("runing", provider)

    ## Option Handling - These might modify the params dict and/or set env vars.
    params["guest_os"] = options.guest_os_option(params.get("guest_os"))
    params["box"] = options.box_option(params.get("box"))
    params["cpus"] = options.cpus_option(params.get("cpus"))
    params["hostname"] = options.hostname_option(params.get("hostname"))
    params["machine_type"] = options.machine_type_option(params.get("machine_type"), params.get("provider"))
    params["project_dir"] = options.project_dir_option(params.get("project_dir"))
    params["provider"] = provider
    params["provision_cmd"] = options.provision_cmd_option(params.get("provision_cmd"))
    params["provision_script"] = options.provision_script_option(params.get("provision_script"))
    params["provision_with_salt"] = options.provision_with_salt_option(params.get("provision_with_salt"))
    params["provision_with_salt_legacy"] = options.provision_with_salt_legacy_option(params.get("provision_with_salt_legacy"))
    params["ram_size"], params["drive_size"] = options.size_option(params.get("ram_size"), params.get("drive_size"))  # both ram and drive size
    params["salt_bootstrap_args"] = options.salt_bootstrap_args_option(params.get("salt_bootstrap_args"))
    params["sync_dirs"] = options.sync_dirs_option(params.get("sync_dirs"))
    params["sync_type"] = options.sync_type_option(params.get("sync_type"))
    params["ports"] = options.ports_option(params.get("ports"))
    params["vm_name"] = options.vm_name_option(params.get("vm_name"))

    if provider not in pure_providers:
        vagrant_up(params, ctx)
    else:
        pure_up(params, ctx)


class Run_app:
    def __init__(self):
        print("in Run_app __init__")
