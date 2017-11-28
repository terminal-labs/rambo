import os
import sys
import json
import click
import pkg_resources
from bash import bash

from rambo.app import (
    destroy,
    export,
    set_init_vars,
    set_vagrant_vars,
    ssh,
    up,
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

## BASE COMMAND LIST
cmd = ''
command_handeled_by_click = ['up','destory','ssh']
if len(sys.argv) > 1:
    cmd = (sys.argv[1])
    if cmd in command_handeled_by_click:
        cmd = ''

context_settings = {
    'ignore_unknown_options': True,
    'allow_extra_args': True,
    'help_option_names': ['-h', '--help'],
}

## Main CLI entry point
@click.group(context_settings=context_settings)
@click.option('--vagrant-cwd', default=None, type=click.Path(),
              help='Path entry point to the Vagrantfile. Defaults to '
              'the Vagrantfile provided by %s in the installed path.'
              % PROJECT_NAME.capitalize())
@click.option('--vagrant-dotfile-path', default=None, type=click.Path(),
              help='Path location of the .vagrant directory for the '
              'virtual machine. Defaults to the current working directory.')
@click.option('--tmpdir-path', default=None, type=click.Path(),
              help='Path location of the .rambo-tmp directory for the virtual'
              ' machine. Defaults to the current working directory')
@click.version_option(prog_name=PROJECT_NAME.capitalize(), version=version)
@click.pass_context
def cli(ctx, vagrant_cwd, vagrant_dotfile_path, tmpdir_path):
    set_init_vars(tmpdir_path)
    set_vagrant_vars(vagrant_cwd, vagrant_dotfile_path)

## Catch-all for everything that doesn't hit a subcommand
@cli.command(name=cmd, context_settings=context_settings)
def gen():
    # TODO: figure out better warning system
    click.echo("Warning -- you entered a command %s does not understand. "
               "Passing raw commands to Vagrant backend" % PROJECT_NAME.capitalize())
    click.echo('You ran "%s"' % ' '.join(sys.argv))
    click.echo('Vagrant backend says:')
    sys.argv.pop(0)
    vagrant_cmd = 'vagrant ' + ' '.join(sys.argv)
    click.echo(bash(vagrant_cmd).stdout)

## Subcommands
@cli.command('destroy')
@click.pass_context
def destroy_cmd(ctx):
    '''Destroy a VM / container and all its metadata. Default leaves logs.
    '''
    destroy(ctx)

@cli.command('export')
@click.option('-f', '--force', is_flag=True)
@click.option('-s', '--salt', '--saltstack', 'src', flag_value='saltstack',
              default=True)
@click.option('-V', '--vagrant', 'src', flag_value='vagrant')
@click.option('-p', '--python', 'src', flag_value='python')
@click.option('-a', '--all', 'src', flag_value='all')
@click.option('-O', '--output-path', type=click.Path(), default=None,
              help='The output path.')
@click.pass_context
def export_cmd(ctx, force, src, output_path):
    '''Export stuff.
    '''
    print('in export_cmd')
    export(ctx, force, src, output_path)

@cli.command('setup')
def setup_cmd(): # threaded setup commands
    '''Runs any setup commands. None yet implemented.
    '''
    # setup_rambo()
    setup_lastpass()

@cli.command('ssh')
@click.pass_context
def ssh_cmd(ctx):
    '''Connect to an running VM / container over ssh.
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


main = cli
