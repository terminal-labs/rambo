import configparser
import os
import sys

import click
import pkg_resources

import rambo.app as app
import rambo.utils as utils
from rambo.settings import CONF_FILES
from rambo.settings import PROJECT_NAME
from rambo.settings import SETTINGS


version = pkg_resources.get_distribution("rambo-vagrant").version


# Only used for the `vagrant` subcommand
VAGRANT_CMD_CONTEXT_SETTINGS = {
    "ignore_unknown_options": True,
    "allow_extra_args": True,
}

# Used for all commands and subcommands
CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"],
    "auto_envvar_prefix": PROJECT_NAME.upper(),
}


# Support for injecting config vars into click context
# https://stackoverflow.com/questions/46358797/python-click-supply-arguments-and-options-from-a-configuration-file
def load_config_for_command(ctx, section):
    parser = configparser.ConfigParser()
    parser.read(CONF_FILES)

    if section == "cli":
        section = "base"
    if section in parser:
        section = parser[section]
        for param, value in ctx.params.items():
            if not value:
                if param in section:
                    if param == "gui":
                        ctx.params[param] = section.getboolean(param)
                    else:
                        ctx.params[param] = section[param]

                    # native_val = parser[section][param]
                    # try:
                    #     native_val = ast.literal_eval(native_val)
                    # except ValueError:
                    #     pass
                    # #     ctx.params[param] = native_val
                    # # else:
                    # #     breakpoint()
                    # #     ctx.params[param] = type(ctx.params[param])(native_val)

                    # ctx_param = ctx.params[param]
                    # if ctx_param is not None:
                    #     ctx.params[param] = type(ctx.params[param])(native_val)
                    # else:
                    #     ctx.params[param] = native_val
    return ctx


class GroupWithConfig(click.Group):
    def invoke(self, ctx):
        ctx = load_config_for_command(ctx, self.name)
        super().invoke(ctx)


class CommandWithConfig(click.Command):
    def invoke(self, ctx):
        ctx = load_config_for_command(ctx, self.name)
        return super().invoke(ctx)


# Main command / CLI entry point
@click.group(context_settings=CONTEXT_SETTINGS, cls=GroupWithConfig)
@click.option(
    "--vagrant-cwd",
    type=click.Path(resolve_path=True),
    help="Path entry point to the Vagrantfile. Defaults to "
    "the Vagrantfile provided by %s in the installed path." % PROJECT_NAME.capitalize(),
)
@click.option(
    "--vagrant-dotfile-path",
    type=click.Path(resolve_path=True),
    help="Path location of the .vagrant directory for the "
    "virtual machine. Defaults to the current working directory.",
)
@click.option(
    "--cwd",
    type=click.Path(resolve_path=True),
    help="The CWD of for this command. Defaults to "
    "actual CWD, but may be set for customization. Used to look "
    "for optional resources such as custom SaltStack code.",
)
@click.option(
    "--tmpdir",
    type=click.Path(resolve_path=True),
    help="Path location of the .rambo-tmp directory for the virtual "
    "machine. Defaults to the current working directory",
)
@click.version_option(prog_name=PROJECT_NAME.capitalize(), version=version)
@click.pass_context
def cli(ctx, cwd, tmpdir, vagrant_cwd, vagrant_dotfile_path):
    """The main cli entry point. Params can be passed as usual with
    click (CLI or env var) and also with an INI config file.
    Precedence is CLI > Config > Env Var > defaults.
    """
    if ctx.invoked_subcommand not in ["createproject"]:
        # These need to be very early because they may change the cwd of this Python or of Vagrant
        app._set_init_vars(cwd, tmpdir)
        app._set_vagrant_vars(vagrant_cwd, vagrant_dotfile_path)

        utils.write_to_log("\nNEW CMD")
        utils.write_to_log(" ".join(sys.argv))

        utils.write_to_log("\nNEW CMD", "stderr")
        utils.write_to_log(" ".join(sys.argv), "stderr")


# Subcommands
@cli.command("createproject")
@click.argument("project_name")
@click.option(
    "-c",
    "--config-only",
    is_flag=True,
    help="Only create project dir with config file.",
)
@click.pass_context
def createproject_cmd(ctx, project_name, config_only):
    """Create project takes an arguement for the name to give to the project
    it creates. It will create a directory in the CWD for this project. Upon
    creation, this project directory will contain a rambo.conf file, an auth
    directory, and a saltstack directory.

    - rambo.conf is the config file that is required to be present in your
        project to run rambo up, and is described later in this document.
    - auth contains some sample scripts that will aid in setting up keys / tokens
        for the cloud providers. It is not required. How to use that is described
        in the cloud provider specific documentation.
    - saltstack is a basic set of SaltStack configuration code that Rambo offers.
        It can be modified for custom configuration.
    """
    app.createproject(
        project_name,
        ctx.parent.params["cwd"],
        ctx.parent.params["tmpdir"],
        config_only,
        ctx,
    )


@cli.command(
    "destroy",
    context_settings=CONTEXT_SETTINGS,
    short_help="Destroy VM and metadata.",
)
@click.option(
    "-v", "--vm_name", type=str, help="The name of the VirtualMachine / Container."
)
@click.pass_context
def destroy_cmd(ctx, vm_name, **params):
    """Destroy a VM / container. This will tell vagrant to forcibly destroy
    a VM, and to also destroy its Rambo metadata (provider and random_tag),
    and Vagrant metadata (.vagrant dir).
    """
    app.destroy(ctx, **ctx.params)


@cli.command("export-vagrant-conf", short_help="Get Vagrant configuration")
@click.option(
    "-f", "--force", is_flag=True, help="Accept attempts to overwrite and merge."
)
@click.option(
    "-O",
    "--output-path",
    type=click.Path(resolve_path=True),
    help="The optional output path.",
)
def export_vagrant_conf(output_path, force):
    """Places the default Vagrantfile and its resources (vagrant dir,
    settings.json) in the CWD for customizing.
    """
    app.export("vagrant", output_path, force)


@cli.command(
    "halt", context_settings=VAGRANT_CMD_CONTEXT_SETTINGS, short_help="Halt VM."
)
@click.pass_context
def halt_cmd(ctx):
    """Tells Vagrant to 'halt' the VM. Useful to free the Host's
    resources without destroying the VM.
    """
    app.halt(ctx)


@cli.command(
    "install-plugins",
    context_settings=CONTEXT_SETTINGS,
    short_help="Install Vagrant plugins",
)
@click.option(
    "-f", "--force", is_flag=True, help="Install plugins without confirmation."
)
@click.argument("plugins", nargs=-1, type=str)
def install_plugins(force, plugins):
    """Install passed args as Vagrant plugins. `all` or no args installs
    all default Vagrant plugins from host platform specific list.
    """
    # If auth and plugins are both not specified, run both.
    if not plugins:  # No args means all default plugins.
        plugins = ("all",)
    app.install_plugins(force, plugins)


@cli.command(
    "scp",
    context_settings=VAGRANT_CMD_CONTEXT_SETTINGS,
    short_help="Transfer files with scp.",
)
@click.pass_context
def scp_cmd(ctx):
    """Transfer files or directories with scp. Accepts two args in one of the
    following forms:

    <local_path> <remote_path>

    <local_path> :<remote_path>

    :<remote_path> <local_path>

    <local_path> [vm_name]:<remote_path>

    [vm_name]:<remote_path> <local_path>

    For example: `rambo scp localfile.txt remotefile.txt`
    """
    app.scp(ctx, ctx.args)


@cli.command("ssh", short_help="Connect with ssh.", cls=CommandWithConfig)
@click.option("-c", "--command", type=str, help="Execute an SSH command directly.")
@click.argument("ssh_args", nargs=-1, type=str)
@click.pass_context
def ssh_cmd(ctx, command, ssh_args):
    """Connect to an running VM / container over ssh. With `-c` / `--command`,
    execute an SSH command directly.

    Supply a final `-- [args]` to pass additional arguments directly to ssh.
    """
    if not ssh_args:
        ssh_args = ctx.params.get("ssh_args")

    app.ssh(ctx, command, ssh_args)


@cli.command(
    "up",
    context_settings=CONTEXT_SETTINGS,
    short_help="Create or start VM.",
    cls=CommandWithConfig,
)
@click.option(
    "-p",
    "--provider",
    type=str,
    help="Provider for the virtual machine. "
    "These providers are supported: %s. Default %s."
    % (SETTINGS["PROVIDERS"], SETTINGS["PROVIDERS_DEFAULT"]),
)
@click.option("--gui", is_flag=True)
@click.option(
    "--res",
    type=str,
    help="Screen resolution if using a gui, of the format '1920x1080'. "
    "Default determined by magic. Ignored if no gui."
)
@click.option(
    "-o",
    "--guest-os",
    type=str,
    help="Operating System of the guest, inside the virtual machine. "
    "These guest OSs are supported: %s. Default %s."
    % (list(SETTINGS["GUEST_OSES"].keys()), SETTINGS["GUEST_OSES_DEFAULT"]),
)
@click.option("-b", "--box", type=str, help="Vagrant Box to use.")
@click.option("--hostname", type=str, help="Hostname to set.")
@click.option(
    "-r",
    "--ram-size",
    type=int,
    help="Amount of RAM of the virtual machine in MB. "
    "These RAM sizes are supported: %s. Default %s."
    % (list(SETTINGS["SIZES"].keys()), SETTINGS["RAMSIZE_DEFAULT"]),
)
@click.option("--cpus", type=int, help="Number of CPUs in a virtualbox VM.")
@click.option(
    "-d",
    "--drive-size",
    type=int,
    help="The drive size of the virtual machine in GB. "
    "These drive sizes are supported: %s. Default %s."
    % (list(SETTINGS["SIZES"].values()), SETTINGS["DRIVESIZE_DEFAULT"]),
)
@click.option(
    "-m",
    "--machine-type",
    type=str,
    help="Machine type for cloud providers.\n"
    "E.g. m5.medium for ec2, or s-8vcpu-32gb for digitalocean.\n",
)
@click.option(
    "--sync-dirs",
    type=str,
    help=(
        "Paths to sync into VM, passed as a Python list of lists of the form "
        """"[['guest_dir', 'host_dir'], ['guest_dir2', 'host_dir2']]"."""
    ),
)
@click.option(
    "--ec2-security-groups",
    type=str,
    help=(
        "A list of security groups to add to the EC2 VM, passed as a Python list of the form "
        """"['salted_server', 'security_group_2]"."""
    ),
)
@click.option("--sync-type", type=str, help="Sync type")
@click.option(
    "--ports",
    type=str,
    help=(
        "Additional ports to sync into VM, passed as a Python list of lists of the form "
        """[['guest_port', 'host_port'], ['guest_port2', 'host_port2']]"."""
    ),
)
@click.option(
    "--ip_address",
    type=str,
    help=("IP address to assign the VM"),
)
@click.option(
    "--project-dir",
    type=click.Path(resolve_path=True),
    help="List of path to sync into VM",
)
@click.option(
    "--provision/--no-provision", default=None, help="Enable or disable provisioning"
)
@click.option("-c", "--command", type=str, help="Command to start provisioning with")
@click.option(
    "--destroy-on-error/--no-destroy-on-error",
    default=None,
    help="Destroy machine if any fatal error happens (default to true)",
)
@click.option("--vm_name", type=str, help=(
    "The name of the VirtualMachine / Container. "
    "This is also the hostname if that wasn't explicitly set."
    )
)
@click.argument("up_args", nargs=-1, type=str)
@click.pass_context
def up_cmd(
    ctx,
    provider,
    box,
    gui,
    res,
    hostname,
    guest_os,
    ram_size,
    cpus,
    drive_size,
    machine_type,
    sync_dirs,
    ec2_security_groups,
    sync_type,
    ports,
    ip_address,
    project_dir,
    provision,
    command,
    destroy_on_error,
    vm_name,
    up_args,
):
    """Start a VM or container. Will create one and begin provisioning it if
    it did not already exist. Accepts many options to set aspects of your VM.
    Precedence is CLI > Config > Env Var > defaults.
    """
    if not os.path.isfile(f"{PROJECT_NAME}.conf"):
        utils.abort(
            f"Config file {PROJECT_NAME}.conf must be present in working directory.\n"
            "A config file is automatically created when you run \n"
            "createproject. You can also make a config file manually."
        )

    app.up(ctx, **ctx.params)


@cli.command(
    "vagrant",
    context_settings=VAGRANT_CMD_CONTEXT_SETTINGS,
    short_help="Run a vagrant command through rambo.",
)
@click.pass_context
def vagrant_cmd(ctx):
    """Accepts any args and forwards them to Vagrant directly, allowing you to
    run any vagrant command. Rambo has first-class duplicates or wrappers for
    the most common Vagrant commands, but for less common commands or commands
    that are not customized, they don't need to be duplicated, so we call them
    directly.
    """
    app.vagrant_general_command(" ".join(ctx.args))


main = cli
