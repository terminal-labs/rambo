import os
import sys
import json

import click
from bash import bash

from rambo.app import setup_lastpass, vagrant_up, vagrant_ssh, vagrant_destroy

## GLOBALS
# Create env var indicating where this code lives. This will be used latter by
# Vagrant as a check that the python cli is being used, as well as being a useful var.
PROJECT_LOCATION = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]
with open(os.path.join(PROJECT_LOCATION, 'rambo/settings.json'), 'r') as f:
    SETTINGS = json.load(f)
PROJECT_NAME = SETTINGS['PROJECT_NAME']
PROVIDERS = SETTINGS['PROVIDERS']

os.environ[PROJECT_NAME.upper() + "_ENV"] = PROJECT_LOCATION
os.environ[PROJECT_NAME.upper() + "_TMP"] = os.path.join(os.getcwd(), '.tmp')
# Vagrant requires the following 2 env vars for custom cwd and dotfile path.
if 'VAGRANT_CWD' not in os.environ: # Where the Vagrantfile and python code are
    os.environ['VAGRANT_CWD'] = PROJECT_LOCATION # (default installed path)
if 'VAGRANT_DOTFILE_PATH' not in os.environ: # Where to put .vagrant dir
    os.environ['VAGRANT_DOTFILE_PATH'] = os.path.normpath(os.path.join(os.getcwd() + '/.vagrant')) # (default cwd)

## BASE COMMAND LIST
cmd = ''
command_handeled_by_click = ['up','destory','ssh']
if len(sys.argv) > 1:
    cmd = (sys.argv[1])
    if cmd in command_handeled_by_click:
        cmd = ''

@click.group()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli(ctx, debug):
    ctx.obj['DEBUG'] = debug

context_settings = {'ignore_unknown_options':True, 'allow_extra_args':True}
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
def up(provider):
    '''
    Call Vagrant up with provider option. Provider may also be supplied by
    the RAMBO_PROVIDER environment variable if not passed as a cli option.
    '''
    # Abort if provider not in whitelist.
    os.environ[PROJECT_NAME.upper() + "_PROVIDER"] = provider
    if provider not in PROVIDERS and provider is not None:
        # TODO See if there's a better exit / error system
        sys.exit('ABORTED - Target provider "%s" is not in the providers '
                 'list. Did you have a typo?' % provider)
    vagrant_up(provider)

@cli.command()
def ssh():
    vagrant_ssh()

@cli.command()
def destroy():
    vagrant_destroy()

@cli.command()
def setup(): # threaded setup commands
    # setup_rambo()
    setup_lastpass()

def main():
    cli(obj={})

if __name__ == '__main__':
    main()
