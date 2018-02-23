import os
import sys
import json
import pkg_resources

from click_configfile import ConfigFileReader, Param, SectionSchema
from click_configfile import matches_section
import click

import rambo.app as app
from rambo.settings import SETTINGS, PROJECT_NAME
from rambo.utils import abort


version = pkg_resources.get_distribution('rambo-vagrant').version


### Config file handling
class ConfigSectionSchema(object):
    '''Describes all config sections of this configuration file.'''

    @matches_section('base')
    class Base(SectionSchema):
        '''Corresponds to the main CLI entry point.'''
        cwd                   = Param(type=click.Path())
        tmpdir_path           = Param(type=click.Path())
        vagrant_cwd           = Param(type=click.Path())
        vagrant_dotfile_path  = Param(type=click.Path())

    @matches_section('up')
    class Up(SectionSchema):
        '''Corresponds to the `up` command group.'''
        provider      = Param(type=str)
        guest_os      = Param(type=str)
        ram_size      = Param(type=int)
        drive_size    = Param(type=int)


class ConfigFileProcessor(ConfigFileReader):
    config_files = ['%s.conf' % PROJECT_NAME]
    # Specify additional schemas to merge with the primary so that they
    # are added to the top level of default_map, for easy precedence of
    # CLI > Configuration file > Environment > Default.
    config_section_primary_schemas = [
        ConfigSectionSchema.Base,
        ConfigSectionSchema.Up,
    ]
    config_section_schemas = config_section_primary_schemas


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
    'auto_envvar_prefix': PROJECT_NAME.upper()
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
    '''The main cli entry point. Params can be passed as usual with
    click (CLI or env var) and also with an INI config file.
    Precedence is CLI > Config > Env Var > defaults.
    '''
    # These need to be very early because they may change the cwd of this Python or of Vagrant
    app.set_init_vars(cwd, tmpdir_path)
    app.set_vagrant_vars(vagrant_cwd, vagrant_dotfile_path)

    app.write_to_log('\nNEW CMD')
    app.write_to_log(' '.join(sys.argv))


### Catch-all for everything that doesn't hit a subcommand
@cli.command(name=cmd, context_settings=dict(CONTEXT_SETTINGS, **BASECMD_CONTEXT_SETTINGS))
def gen():
    # TODO: figure out better warning system
    click.echo("Warning -- you entered a command %s does not understand. "
               "Passing raw commands to Vagrant backend" % PROJECT_NAME.capitalize())
    click.echo('You ran "%s"' % ' '.join(sys.argv))
    sys.argv.pop(0) # Remove Rambo path from full command
    click.echo('Vagrant backend says:')
    app.vagrant_general_command(' '.join(sys.argv))


### Subcommands
@cli.command('createproject')
@click.argument('project_name')
def createproject_cmd(project_name):
    '''Create a Rambo project dir with basic setup.
    '''
    app.createproject(project_name)


@cli.command('destroy')
@click.pass_context
def destroy_cmd(ctx):
    '''Destroy a VM / container and all its metadata. Default leaves logs.
    '''
    app.destroy(ctx)


@cli.command('export-vagrant-conf', short_help="Get Vagrant configuration")
@click.option('-f', '--force', is_flag=True,
              help='Accept attempts to overwrite and merge.')
@click.option('-O', '--output-path', type=click.Path(), default=None,
              help='The optional output path.')
def export_vagrant_conf(output_path, force):
    '''Export Vagrant configuration to your project for customization.
    '''
    app.export('vagrant', output_path, force)


@cli.command('install-plugins', context_settings=CONTEXT_SETTINGS)
@click.option('-f', '--force', is_flag=True,
              help='Install plugins without confirmation.')
@click.argument('plugins', nargs=-1, type=str)
def install_plugins(force, plugins):
    '''Install passed args as vagrant plugins. `all` or no args installs
    all default vagrant plugins.
    '''
    # If auth and plugins are both not specified, run both.
    if not plugins: # No args means all default plugins.
        plugins = ('all',)
    app.install_plugins(force, plugins)


@cli.command('ssh', short_help="Connect with `vagrant ssh`")
@click.pass_context
def ssh_cmd(ctx):
    '''Connect to an running VM / container over ssh with `vagrant ssh`.
    '''
    app.ssh(ctx)


@cli.command('up', context_settings=CONTEXT_SETTINGS)
@click.option('-p', '--provider', type=str,
              help='Provider for the virtual machine. '
              'These providers are supported: %s. Default %s.'
              % (SETTINGS['PROVIDERS'], SETTINGS['PROVIDERS_DEFAULT']))
@click.option('-o', '--guest-os', type=str,
              help='Operating System of the guest, inside the virtual machine. '
              'These guest OSs are supported: %s. Default %s.'
              % (list(SETTINGS['GUEST_OSES'].keys()),
                 SETTINGS['GUEST_OSES_DEFAULT']))
@click.option('-r', '--ram-size', type=int,
              help='Amount of RAM of the virtual machine in MB. '
              'These RAM sizes are supported: %s. Default %s.'
              % (list(SETTINGS['SIZES'].keys()),
                 SETTINGS['RAMSIZE_DEFAULT']))
@click.option('-d', '--drive-size', type=int,
              help='The drive size of the virtual machine in GB. '
              'These drive sizes are supported: %s. Default %s.'
              % (list(SETTINGS['SIZES'].values()),
                 SETTINGS['DRIVESIZE_DEFAULT']))
@click.pass_context
def up_cmd(ctx, provider, guest_os, ram_size, drive_size):
    '''Start a VM / container with `vagrant up`.
    Params can be passed as usual with
    click (CLI or env var) and also with an INI config file.
    Precedence is CLI > Config > Env Var > defaults.
    '''
    if not os.path.isfile('%s.conf' % PROJECT_NAME):
        abort("Config file %s.conf must be present in working directory.\n"
              "You can create one with `%s setup config`." %
              (PROJECT_NAME, PROJECT_NAME))

    app.up(ctx, provider, guest_os, ram_size, drive_size)

main = cli
