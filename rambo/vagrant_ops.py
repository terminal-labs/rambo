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
from rambo.utils import get_env_var, set_env_var


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
    cmd = " ".join(["vagrant", cmd]).split()

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


def vagrant_general_command(cmd):
    """Invoke vagrant with custom command.

    Args:
        cmd (str): String to append to command `vagrant ...`
    """
    # Modify cmd in private function to keep enforcement of being a vagrant cmd there.
    return _invoke_vagrant(cmd)


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
                click.confirm('The plugin "%s" is not in our list of plugins. Attempt ' "to install anyway?" % plugin, abort=True)
            vagrant_general_command("plugin install %s" % plugin)


def set_vagrant_vars(vagrant_cwd=None, vagrant_dotfile_path=None):
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
        os.environ["VAGRANT_DOTFILE_PATH"] = os.path.normpath(os.path.join(os.getcwd(), ".vagrant"))  # default (cwd)


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
    set_env_var("ENV", PROJECT_LOCATION)  # installed location of this code


## Defs used by main cli cmd
def set_cwd(cwd=None):
    """Set cwd environment variable and change the actual cwd to it.

    Args:
        cwd (path): Location of project (conf file, provisioning scripts, etc.).
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


def set_tmpdir(tmpdir=None):
    """Set tmpdir and log_path locations. This should defaut to be inside the cwd.

    Args:
        tmpdir (path): Location of project's tmp dir.
    """
    # loc of tmpdir
    if tmpdir:  # cli / api
        set_env_var("TMPDIR", tmpdir)
    elif get_env_var("TMPDIR"):  # Previously set env var
        set_env_var("TMPDIR", os.path.join(get_env_var("TMPDIR"), ".%s-tmp" % PROJECT_NAME))
    else:  # Not set, set to default loc
        set_env_var("TMPDIR", os.path.join(os.getcwd(), ".%s-tmp" % PROJECT_NAME))  # default (cwd)

    set_env_var("LOG_PATH", os.path.join(get_env_var("TMPDIR"), "logs"))


def vagrant_up(params, ctx):
    cmd = "up"
    ## Provider specific handling.
    ## Must come after all else, because logic may be done on params above.
    if params["provider"] == "digitalocean":
        vagrant_providers.digitalocean()
    elif params["provider"] == "docker":
        vagrant_providers.docker()
    elif params["provider"] == "ec2":
        vagrant_providers.ec2(**params)
    else:
        cmd += " --provider={}".format(params["provider"])

    ## Add straight pass-through flags. Keep test for True/False explicit as only those values should work
    if params.get("provision") is True:
        cmd = "{} {}".format(cmd, "--provision")
    elif params.get("provision") is False:
        cmd = "{} {}".format(cmd, "--no-provision")

    if params.get("destroy_on_error") is True:
        cmd = "{} {}".format(cmd, "--destroy-on-error")
    elif params.get("destroy_on_error") is False:
        cmd = "{} {}".format(cmd, "--no-destroy-on-error")

    vagrant_general_command(cmd)


def vagrant_halt(ctx, args, params):
    if not ctx:  # Using API. Else handled by cli.
        set_init_vars(params.get("cwd"), params.get("tmpdir"))
        set_vagrant_vars(params.get("vagrant_cwd"), params.get("vagrant_dotfile_path"))
    else:
        args = ctx.args + list(args)

    vagrant_general_command("{} {}".format("halt", " ".join(args)))
