import os
import sys
import json
import click
from bash import bash

from rambo.app import vagrant_up, vagrant_ssh, vagrant_destroy, set_init_vars, set_vagrant_vars

## GLOBALS
# Create env var indicating where this code lives. This will be used latter by
# Vagrant as a check that the python cli is being used, as well as being a useful var.
PROJECT_LOCATION = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(PROJECT_LOCATION, 'settings.json'), 'r') as f:
    SETTINGS = json.load(f)
PROVIDERS = SETTINGS['PROVIDERS']
PROJECT_NAME = SETTINGS['PROJECT_NAME']

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

@click.group(context_settings=context_settings)
@click.option('--vagrant-cwd', default=None, type=click.Path(),
              help='Path entry point to the Vagrantfile. Defaults to '
              'the Vagrantfile provided by %s in the installed path.'
              % PROJECT_NAME.capitalize())
@click.option('--vagrant-dotfile-path', default=None, type=click.Path(),
              help='Path location of the .vagrant directory for the '
              'virtual machine. Defaults to the current working directory.')
@click.pass_context
def cli(ctx, vagrant_cwd, vagrant_dotfile_path):
    set_init_vars()
    set_vagrant_vars(vagrant_cwd, vagrant_dotfile_path)

@cli.command(name=cmd, context_settings=context_settings)
def gen():
    # TODO: figure out better warning system
    click.echo("warning -- you entered a command " + PROJECT_NAME  +
               " does not understand. passing raw commands to vagrant backend")
    click.echo('You ran "' + ' '.join(sys.argv) + '"')
    click.echo('Vagrant backend says:')
    sys.argv.pop(0)
    vagrant_cmd = 'vagrant ' + ' '.join(sys.argv)
    click.echo(bash(vagrant_cmd).stdout)

@cli.command()
@click.option('-p', '--provider', envvar = PROJECT_NAME.upper() + '_PROVIDER',
              help='Provider for the virtual machine. '
              'These providers are supported: %s. Default virtualbox.' % PROVIDERS)
@click.pass_context
def up(ctx, provider):
    '''Start a VM / container with `vagrant up`.
    '''
    vagrant_up(ctx, provider)

@cli.command()
@click.pass_context
def ssh(ctx):
    '''Connect to an running VM / container over ssh.
    '''
    vagrant_ssh()

@cli.command()
@click.pass_context
def destroy(ctx):
    '''Destroy a VM / container and all its metadata. Default leaves logs.
    '''
    vagrant_destroy()

@cli.command()
def setup(): # threaded setup commands
    '''Runs any setup commands. None yet implemented.
    '''
    # setup_rambo()
    setup_lastpass()

main = cli
