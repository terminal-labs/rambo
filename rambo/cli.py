import os
import sys
import json
import click
import pkg_resources

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

## GLOBALS
# Create env var indicating where this code lives. This will be used latter by
# Vagrant as a check that the python cli is being used, as well as being a useful var.
PROJECT_LOCATION = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(PROJECT_LOCATION, 'settings.json'), 'r') as f:
    SETTINGS = json.load(f)
PROVIDERS = SETTINGS['PROVIDERS']
PROJECT_NAME = SETTINGS['PROJECT_NAME']

version = pkg_resources.get_distribution('rambo-vagrant').version

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

context_settings = {
    'ignore_unknown_options': True,
    'allow_extra_args': True,
    'help_option_names': ['-h', '--help'],
}

### Main command / CLI entry point
@click.group(context_settings=context_settings)
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
              help='Path location of the .rambo-tmp directory for the virtual'
              ' machine. Defaults to the current working directory')
@click.version_option(prog_name=PROJECT_NAME.capitalize(), version=version)
@click.pass_context
def cli(ctx, vagrant_cwd, vagrant_dotfile_path, cwd, tmpdir_path):
    set_init_vars(cwd, tmpdir_path)
    set_vagrant_vars(vagrant_cwd, vagrant_dotfile_path)

    write_to_log('\nNEW CMD')
    write_to_log(' '.join(sys.argv))

### Catch-all for everything that doesn't hit a subcommand
@cli.command(name=cmd, context_settings=context_settings)
def gen():
    # TODO: figure out better warning system
    click.echo("Warning -- you entered a command %s does not understand. "
               "Passing raw commands to Vagrant backend" % PROJECT_NAME.capitalize())
    click.echo('You ran "%s"' % ' '.join(sys.argv))
    click.echo('Vagrant backend says:')
    vagrant_general_command(sys.argv.pop(0))

### Subcommands
@cli.command('createproject')
@click.option('-P', '--project-path', type=click.Path(), default=None,
              help='The project path (optional).')
@click.argument('project_name')
@click.pass_context
def createproject_cmd(ctx, project_name, project_path):
    '''Create a Rambo project dir with basic setup.
    '''
    createproject(ctx, project_name, project_path)

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

@cli.command('up')
@click.option('-p', '--provider', envvar = PROJECT_NAME.upper() + '_PROVIDER',
              help='Provider for the virtual machine. '
              'These providers are supported: %s. Default virtualbox.' % PROVIDERS)
@click.pass_context
def up_cmd(ctx, provider):
    '''Start a VM / container with `vagrant up`.
    '''
    up(ctx, provider)

### Sub-subcommands
## subcommands of setup_cmd
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

@setup_cmd.command('auth')
@click.option('-O', '--output-path', type=click.Path(), default=None,
              help='The optional output path.')
def auth_cmd(output_path):
    '''Install auth directory.
    '''
    install_auth(output_path)

main = cli
