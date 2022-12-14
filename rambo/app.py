import errno
import os
import platform
import pty
import shutil
import sys
from pathlib import Path
from select import select
from subprocess import Popen

import click
from distutils.dir_util import copy_tree
from distutils.errors import DistutilsFileError

import rambo.options as options
import rambo.utils as utils
import rambo.vagrant_providers as vagrant_providers
from rambo.settings import PROJECT_LOCATION
from rambo.settings import PROJECT_NAME
from rambo.settings import SETTINGS
from rambo.utils import abort
from rambo.utils import get_env_var
from rambo.utils import set_env_var

VAGRANT_EXE = os.getenv("VAGRANT_EXE", "vagrant")

def _invoke_vagrant(cmd=None):
    """Pass a command to vagrant. This outputs in near real-time,
    logs both stderr and stdout in a combined file, and detects stderr for
    our own error handling.

    Returns returncode (exitcode) of the command.

    Args:
        cmd (str): The cmd string that is appended to `vagrant ...`,
                   passed to the shell and executed.
    """
    masters, slaves = zip(pty.openpty(), pty.openpty())
    cmd = " ".join([VAGRANT_EXE, cmd]).split()

    with Popen(cmd, stdin=slaves[0], stdout=slaves[0], stderr=slaves[1]) as p:
        for fd in slaves:
            os.close(fd)  # no input
            readable = {
                masters[0]: sys.stdout.buffer,  # store buffers seperately
                masters[1]: sys.stderr.buffer,
            }
        while readable:
            for fd in select(readable, [], [])[0]:
                try:
                    data = os.read(fd, 1024)  # read available
                except OSError as e:
                    if e.errno != errno.EIO:
                        raise  # XXX cleanup
                    del readable[fd]  # EIO means EOF on some systems
                else:
                    if not data:  # EOF
                        del readable[fd]
                    else:
                        if fd == masters[0]:  # We caught stdout
                            utils.echo(data.rstrip())
                            utils.write_to_log(data)
                        else:  # We caught stderr
                            utils.echo(data.rstrip(), err=True)
                            utils.write_to_log(data, "stderr")
                        readable[fd].flush()
    for fd in masters:
        os.close(fd)
    return p.returncode


def _set_init_vars(cwd=None, tmpdir=None):
    """Set env vars that are used throughout Ruby and Python. If Ruby weren't used
    this would be managed very differently, as these are effectively project scoped
    global variables.

    These calls are split into separate functions because on occaision we need to call
    them more carefully than with this function, as in createproject.
    """
    _set_env()
    _set_cwd(cwd)
    _set_tmpdir(tmpdir)


def _set_env():
    set_env_var("ENV", PROJECT_LOCATION)  # installed location of this code


# Defs used by main cli cmd
def _set_cwd(cwd=None):
    """Set cwd environment variable and change the actual cwd to it.

    Args:
        cwd (path): Location of project (conf file, provisioning scripts, etc.)
    """
    # effective CWD (likely real CWD, but may be changed by user.
    if cwd:  # cli / api
        set_env_var("cwd", cwd)
    elif get_env_var("cwd"):
        pass  # Already set - keep it.
    else:
        found_project = utils.find_conf(os.getcwd())
        if found_project:
            set_env_var("cwd", found_project)
        else:
            set_env_var("cwd", os.getcwd())

    os.chdir(get_env_var("cwd"))
    return get_env_var("cwd")


def _set_tmpdir(tmpdir=None):
    """Set tmpdir and log_path locations. This should defaut to be inside the cwd.

    Args:
        tmpdir (path): Location of project's tmp dir.
    """
    # loc of tmpdir
    if tmpdir:  # cli / api
        set_env_var("TMPDIR", os.path.join(tmpdir, ".%s-tmp" % PROJECT_NAME))
    elif get_env_var("TMPDIR"):  # Previously set env var
        set_env_var(
            "TMPDIR", os.path.join(get_env_var("TMPDIR"), ".%s-tmp" % PROJECT_NAME)
        )
    else:  # Not set, set to default loc
        set_env_var(
            "TMPDIR", os.path.join(os.getcwd(), ".%s-tmp" % PROJECT_NAME)
        )  # default (cwd)

    set_env_var("LOG_PATH", os.path.join(get_env_var("TMPDIR"), "logs"))


def _set_vagrant_vars(vagrant_cwd=None, vagrant_dotfile_path=None):
    """Set the environment varialbes prefixed with `VAGRANT_` that vagrant
    expects, and that we use, to modify some use paths.

    Agrs:
        vagrant_cwd (path): Location of `Vagrantfile`. Used if invoked with API only.
        vagrant_dotfile_path (path): Location of `.vagrant` metadata directory. Used if invoked with API only.
    """
    # loc of Vagrantfile
    if vagrant_cwd:  # cli / api
        os.environ["VAGRANT_CWD"] = vagrant_cwd
    elif "VAGRANT_CWD" not in os.environ:  # Not set in env var
        # if custom Vagrantfile exists in the default location.
        if os.path.isfile(os.path.join(os.getcwd(), "Vagrantfile")):
            os.environ["VAGRANT_CWD"] = os.getcwd()
        else:  # use default (installed) path
            os.environ["VAGRANT_CWD"] = PROJECT_LOCATION
    # loc of .vagrant dir
    if vagrant_dotfile_path:  # cli / api
        os.environ["VAGRANT_DOTFILE_PATH"] = vagrant_dotfile_path
    elif "VAGRANT_DOTFILE_PATH" not in os.environ:  # Not set in env var
        os.environ["VAGRANT_DOTFILE_PATH"] = os.path.normpath(
            os.path.join(os.getcwd(), ".vagrant")
        )  # default (cwd)


# Defs for cli subcommands
def createproject(project_name, cwd, tmpdir, config_only=None, ctx=None):
    """Create project with basic configuration files.

    Agrs:
        project_name (path): Place to create a new project. Must be non-existing dir.
        config_only (bool): Determins if we should only place a conf file in the new project.
    """
    # initialize paths
    _set_env()
    cwd = _set_cwd(cwd)
    path = os.path.join(cwd, project_name)
    _set_tmpdir(path)

    # create new project dir
    try:
        os.makedirs(path)  # Make parent dirs if needed.
    except FileExistsError:
        utils.abort("Directory already exists.")
    utils.echo(
        'Created %s project "%s" in %s.'
        % (PROJECT_NAME.capitalize(), project_name, path)
    )

    # Fill project dir with basic configs.
    install_config(ctx, output_path=path)
    install_gitignore(ctx, output_path=path)
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
        _set_init_vars(params.get("cwd"), params.get("tmpdir"))
        _set_vagrant_vars(params.get("vagrant_cwd"), params.get("vagrant_dotfile_path"))

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
                        "One or more destination files or directories in "
                        "'%s' already exists. Attempt to merge and "
                        "overwrite?" % dsts,
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
                os.makedirs(
                    os.path.dirname(dst), exist_ok=True
                )  # Make parent dirs if needed. # Py 3.2+
                shutil.copy(src, dst)  # Copy file with overwrites.

    utils.echo("Done exporting %s code." % resource)


def halt(ctx=None, *args, **params):
    if not ctx:  # Using API. Else handled by cli.
        _set_init_vars(params.get("cwd"), params.get("tmpdir"))
        _set_vagrant_vars(params.get("vagrant_cwd"), params.get("vagrant_dotfile_path"))
    else:
        args = ctx.args + list(args)

    vagrant_general_command("{} {}".format("halt", " ".join(args)))


def install_auth(ctx=None, output_path=None, **kwargs):
    """Install auth directory.

    Agrs:
        ctx (object): Click Context object.
        output_path (path): Path to place auth dir.
    """
    if not ctx:  # Using API. Else handled by cli.
        _set_init_vars(kwargs.get("cwd"), kwargs.get("tmpdir"))

    if not output_path:
        output_path = get_env_var("cwd")
    license_dir = os.path.join(output_path, "auth/licenses")
    try:
        os.makedirs(license_dir)
    except FileExistsError:
        pass  # Dir already created. Moving on.
    utils.echo(
        "Any (license) files you put in %s will be synced into your VM." % license_dir
    )

    for filename in os.listdir(os.path.join(get_env_var("env"), "auth/env_scripts")):
        dst_dir = os.path.join(output_path, "auth/keys")
        dst = os.path.join(dst_dir, os.path.splitext(filename)[0])
        if not os.path.isfile(dst):
            os.makedirs(dst_dir, exist_ok=True)  # Make parent dirs if needed. # Py 3.2+
            shutil.copy(
                os.path.join(get_env_var("env"), "auth/env_scripts", filename), dst
            )
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
        _set_init_vars(kwargs.get("cwd"), kwargs.get("tmpdir"))

    if not output_path:
        output_path = get_env_var("cwd")
    path = os.path.join(output_path, "%s.conf" % PROJECT_NAME)

    if os.path.exists(path):
        utils.abort("%s.conf already esists." % PROJECT_NAME)
    else:
        with open(path, "w") as f:
            f.write(
                """\
[up]
provider = virtualbox
box = ubuntu/bionic64
sync_dirs = [["saltstack/etc", "/etc/salt"], ["saltstack/srv", "/srv"]]
"""
            )
        utils.echo("Created config at %s" % path)


def install_gitignore(ctx=None, output_path=None, **kwargs):
    """Install config file.

    Agrs:
        ctx (object): Click Context object.
        output_path (path): Path to place conf file.
    """
    if not ctx:  # Using API. Else handled by cli.
        _set_init_vars(kwargs.get("cwd"), kwargs.get("tmpdir"))

    if not output_path:
        output_path = get_env_var("cwd")
    path = os.path.join(output_path, ".gitignore")

    if os.path.exists(path):
        pass
    else:
        with open(path, "w") as f:
            f.write(
                """\
.rambo-tmp/
.vagrant/
my_rambo.conf
auth/
"""
            )
        utils.echo("Created .gitignore")


def install_plugins(force=None, plugins=("all",)):
    """Install all of the vagrant plugins needed for all plugins

    Agrs:
        force (bool): Forces bypassing of reinstallation prompt.
        plugins (tuple): Names of vagrant plugins to install.
    """
    host_system = platform.system()
    for plugin in plugins:
        if plugin == "all":
            utils.echo("Installing all default plugins.")
            for plugin in SETTINGS["PLUGINS"][host_system]:
                _invoke_vagrant("plugin install %s" % plugin)
        elif plugin in SETTINGS["PLUGINS"][host_system]:
            _invoke_vagrant("plugin install %s" % plugin)
        else:
            if not force:
                click.confirm(
                    'The plugin "%s" is not in our list of plugins. Attempt '
                    "to install anyway?" % plugin,
                    abort=True,
                )
            vagrant_general_command("plugin install %s" % plugin)


def scp(ctx=None, locations=None, **params):
    """Transfer file or dir with scp. This makes use of the vagrant-scp plugin,
    which allows for simplified args.
    """
    if not ctx:  # Using API. Else handled by cli.
        _set_init_vars(params.get("cwd"), params.get("tmpdir"))
        _set_vagrant_vars(params.get("vagrant_cwd"), params.get("vagrant_dotfile_path"))

    if len(locations) != 2:
        utils.abort(
            "There needs to be exactly two arguments for scp, a 'from' location "
            "and a 'to' location.\nYou gave: %s." % " ".join(locations)
        )

    copy_from = locations[0]
    copy_to = locations[1]

    if ":" in copy_from:  # copy_from is remote, fix copy_to which is local
        copy_to = os.path.abspath(copy_to)
    else:  # if no ':' in copy_from, copy_to must be remote, fix copy_from which is local
        copy_from = os.path.abspath(copy_from)

    locations = [copy_from, copy_to]

    vagrant_general_command("{} {}".format("scp", " ".join(locations)))


def ssh(ctx=None, command=None, ssh_args=None, **params):
    """Connect to an running VM / container over ssh.
    All str args can also be set as an environment variable; arg takes precedence.

    Agrs:
        ctx (object): Click Context object.
        command (str): Pass-through command to run with `vagrant ssh --command`.
        vagrant_cwd (path): Location of `Vagrantfile`. Used if invoked with API only.
        vagrant_dotfile_path (path): Location of `.vagrant` metadata directory. Used if invoked with API only.
    """
    if not ctx:  # Using API. Else handled by cli.
        _set_init_vars(params.get("cwd"), params.get("tmpdir"))
        _set_vagrant_vars(params.get("vagrant_cwd"), params.get("vagrant_dotfile_path"))

    # Add pass-through 'command' option.
    cmd = f"{VAGRANT_EXE} ssh"
    if command:
        cmd = " ".join([cmd, "--command", command])

    if ssh_args:
        cmd = f"{cmd} -- {' '.join(ssh_args)}"

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
        command (str): Command used at beginning of provisioning.
        destroy_on_error (bool): vagrant destroy-on-error flag.
        vagrant_cwd (path): Location of `Vagrantfile`. Used if invoked with API only.
        vagrant_dotfile_path (path): Location of `.vagrant` metadata directory. Used if invoked with API only.
        vm_name (str): Name of the VM or container.
    """
    # TODO: Add registering of VM for all of this installation to see
    if not ctx:  # Using API. Else handled by cli.
        _set_init_vars(params.get("cwd"), params.get("tmpdir"))
        _set_vagrant_vars(params.get("vagrant_cwd"), params.get("vagrant_dotfile_path"))

    # Option Handling - These might modify the params dict and/or set env vars.
    params["guest_os"] = options.guest_os_option(params.get("guest_os"))
    params["box"] = options.box_option(params.get("box"))
    params["cpus"] = options.cpus_option(params.get("cpus"))
    params["hostname"] = options.hostname_option(params.get("hostname"))
    params["machine_type"] = options.machine_type_option(
        params.get("machine_type"), params.get("provider")
    )
    params["project_dir"] = options.project_dir_option(params.get("project_dir"))
    params["provider"] = options.provider_option(params.get("provider"))
    params["command"] = options.command_option(params.get("command"))
    params["ram_size"], params["drive_size"] = options.size_option(
        params.get("ram_size"), params.get("drive_size")
    )  # both ram and drive size
    params["sync_dirs"] = options.sync_dirs_option(params.get("sync_dirs"))
    params["sync_type"] = options.sync_type_option(params.get("sync_type"))
    params["ports"] = options.ports_option(params.get("ports"))
    params["vm_name"] = options.vm_name_option(params.get("vm_name"))

    cmd = "up"

    # Provider specific handling.
    # Must come after all else, because logic may be done on params above.
    if params["provider"] == "digitalocean":
        vagrant_providers.digitalocean()
    elif params["provider"] == "docker":
        vagrant_providers.docker()
    elif params["provider"] == "ec2":
        vagrant_providers.ec2(**params)
    else:
        cmd += " --provider={}".format(params["provider"])

    # Add straight pass-through flags. Keep test for True/False explicit as only those values should work
    if params.get("provision") is True:
        cmd = "{} {}".format(cmd, "--provision")
    elif params.get("provision") is False:
        cmd = "{} {}".format(cmd, "--no-provision")

    if params.get("destroy_on_error") is True:
        cmd = "{} {}".format(cmd, "--destroy-on-error")
    elif params.get("destroy_on_error") is False:
        cmd = "{} {}".format(cmd, "--no-destroy-on-error")

    exit_code = vagrant_general_command(cmd)

    if exit_code:
        with open(Path(get_env_var("LOG_PATH")) / "stderr.log") as fp:
            stderr = fp.readlines()
        for idx, line in enumerate(reversed(stderr)):
            if "Unknown configuration section 'disksize'" in line:
                abort(
                    "You probably don't have plugins installed.\nRun:\n"
                    "\trambo install-plugins"
                )
            elif idx > 5:
                # Only look through the recent stderr.
                break


def vagrant_general_command(cmd):
    """Invoke vagrant with custom command.

    Args:
        cmd (str): String to append to command `vagrant ...`
    """
    # Modify cmd in private function to keep enforcement of being a vagrant cmd there.
    return _invoke_vagrant(cmd)
