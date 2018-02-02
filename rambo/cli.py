import os
import sys
import json
import pkg_resources

from click_configfile import ConfigFileReader, Param, SectionSchema
from click_configfile import matches_section
import click

from rambo.utils import abort
from rambo.app import (
    createproject,
    destroy,
    export,
    setup,
    install_auth,
    install_plugins,
    set_init_vars,
    set_vagrant_vars,
    ssh,
    up,
    vagrant_general_command,
    write_to_log,
)

### GLOBALS
# Create env var indicating where this code lives. This will be used latter by
# Vagrant as a check that the python cli is being used, as well as being a useful var.
PROJECT_LOCATION = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(PROJECT_LOCATION, 'settings.json'), 'r') as f:
    SETTINGS = json.load(f)
PROVIDERS = SETTINGS['PROVIDERS']
GUEST_OSES = SETTINGS['GUEST_OSES']
PROJECT_NAME = SETTINGS['PROJECT_NAME']

version = pkg_resources.get_distribution('rambo-vagrant').version

### Config file handling
class ConfigSectionSchema(object):
    """Describes all config sections of this configuration file."""

    @matches_section("base")
    class Base(SectionSchema):
        cwd                   = Param(type=click.Path())
        tmpdir_path           = Param(type=click.Path())
        vagrant_cwd           = Param(type=click.Path())
        vagrant_dotfile_path  = Param(type=click.Path())

    @matches_section("up")
    class Up(SectionSchema):
        provider    = Param(type=str)
        guest_os    = Param(type=str)

class ConfigFileProcessor(ConfigFileReader):
    config_files = ['rambo.ini', 'rambo.cfg', 'rambo.conf']
    config_section_schemas = [
        ConfigSectionSchema.Base,
        ConfigSectionSchema.Up,
    ]

### BASE COMMAND LIST
cmd = ''
commands_handled_by_click = [
    'destory_cmd',
    'export_cmd',
    'ssh_cmd',
    'up_cmd',
]
if len(sys.argv) > 1:
    cmd = (sys.argv[1])
    if cmd in commands_handled_by_click:
        cmd = ''

# Only used for the base command and not any subcommands
BASECMD_CONTEXT_SETTINGS = {
    'ignore_unknown_options': True,
    'allow_extra_args': True,
}

# Used for all commands and subcommands
CONTEXT_SETTINGS = {
    'help_option_names': ['-h', '--help'],
    'default_map': ConfigFileProcessor.read_config(),
}

### Main command / CLI entry point
@click.group(context_settings=dict(CONTEXT_SETTINGS, **BASECMD_CONTEXT_SETTINGS))
@click.option('--vagrant-cwd', default=None, type=click.Path(),
              help='Path entry point to the Vagrantfile. Defaults to '
              'the Vagrantfile provided by %s in the installed path.'
              % PROJECT_NAME.capitalize())
@click.option('--vagrant-dotfile-path', default=None, type=click.Path(),
              help='Path location of the .vagrant directory for the '
              'virtual machine. Defaults to the current working directory.')
@click.option('--cwd', default=None, type=click.Path(),
              help='The CWD of for this command. Defaults to '
              'actual CWD, but may be set for customization. Used to look '
              'for optional resources such as custom SaltStack code.')
@click.option('--tmpdir-path', default=None, type=click.Path(),
              help='Path location of the .rambo-tmp directory for the virtual '
              'machine. Defaults to the current working directory')
@click.version_option(prog_name=PROJECT_NAME.capitalize(), version=version)
@click.pass_context
def cli(ctx, cwd, tmpdir_path, vagrant_cwd, vagrant_dotfile_path):
    # These need to be very early because they may change the cwd of this Python or of Vagrant
    set_init_vars(cwd, tmpdir_path)
    set_vagrant_vars(vagrant_cwd, vagrant_dotfile_path)

    write_to_log('\nNEW CMD')
    write_to_log(' '.join(sys.argv))

### Catch-all for everything that doesn't hit a subcommand
@cli.command(name=cmd, context_settings=dict(CONTEXT_SETTINGS, **BASECMD_CONTEXT_SETTINGS))
def gen():
    # TODO: figure out better warning system
    click.echo("Warning -- you entered a command %s does not understand. "
               "Passing raw commands to Vagrant backend" % PROJECT_NAME.capitalize())
    click.echo('You ran "%s"' % ' '.join(sys.argv))
    sys.argv.pop(0) # Remove Rambo path from full command
    click.echo('Vagrant backend says:')
    vagrant_general_command(' '.join(sys.argv))

### Subcommands
@cli.command('createproject')
@click.argument('project_name')
def createproject_cmd(project_name):
    '''Create a Rambo project dir with basic setup.
    '''
    createproject(project_name)

@cli.command('destroy')
@click.pass_context
def destroy_cmd(ctx):
    '''Destroy a VM / container and all its metadata. Default leaves logs.
    '''
    destroy(ctx)

@cli.command('export', short_help="Export %s's source code." % PROJECT_NAME.capitalize())
@click.option('-f', '--force', is_flag=True,
              help='Accept attempts to overwrite and merge.')
@click.option('-s', '--salt', '--saltstack', 'src', flag_value='saltstack',
              default=True, help='Export SaltStack code.' )
@click.option('-V', '--vagrant', 'src', flag_value='vagrant',
              help='Export Vagrant code.')
@click.option('-p', '--python', 'src', flag_value='python',
              help='Export Python code.')
@click.option('-a', '--all', 'src', flag_value='all',
              help="Export all of %s's project code." % PROJECT_NAME.capitalize())
@click.option('-O', '--output-path', type=click.Path(), default=None,
              help='The optional output path.')
def export_cmd(src, output_path, force):
    '''Export code to a handy place for the user to view and edit.
    '''
    export(src, output_path, force)

@cli.group('setup', invoke_without_command=True)
@click.pass_context
def setup_cmd(ctx):
    '''Create basic auth files and install dependencies (like Vagrant plugins).
    '''
    # If auth and plugins are both not specified, run both.
    if ctx.invoked_subcommand is None:
        setup()

@cli.command('ssh', short_help="Connect with `vagrant ssh`")
@click.pass_context
def ssh_cmd(ctx):
    '''Connect to an running VM / container over ssh with `vagrant ssh`.
    '''
    ssh(ctx)

@cli.command('up', context_settings=CONTEXT_SETTINGS)
@click.option('-p', '--provider', envvar = PROJECT_NAME.upper() + '_PROVIDER',
              help='Provider for the virtual machine. '
              'These providers are supported: %s. Default virtualbox.' % PROVIDERS)
@click.option('-o', '--guest-os', envvar = PROJECT_NAME.upper() + '_GUEST_OS',
              help='Operating System of the guest, inside the virtual machine. '
              'These guest OSs are supported: %s. Default Ubuntu.' % GUEST_OSES)
@click.pass_context
def up_cmd(ctx, provider, guest_os):
    '''Start a VM / container with `vagrant up`.
    '''
    up(ctx, provider, guest_os)

### Sub-subcommands
## subcommands of setup_cmd
@setup_cmd.command('auth')
@click.pass_context
def auth_cmd(ctx):
    '''Install auth directory.
    '''
    install_auth(ctx)

@setup_cmd.command('config')
@click.pass_context
def config_cmd(ctx):
    '''Install config file.
    '''
    install_config(ctx)

@setup_cmd.command('plugins')
@click.option('-f', '--force', is_flag=True,
              help='Install plugins without confirmation.')
@click.argument('plugins', nargs=-1, type=str)
def plugins_cmd(force, plugins):
    '''Install passed args as vagrant plugins. `all` or no args installs
    all default vagrant plugins.
    '''
    if not plugins: # No args means all default plugins.
        plugins = ('all',)
    install_plugins(force, plugins)

main = cli
