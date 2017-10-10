import os
import sys
import json

import click
from bash import bash

from rambo.app import setup_lastpass, vagrant_up, vagrant_ssh, vagrant_destroy

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


def set_env_var(name, value):
    '''
    Set an environment variable in all caps that is prefixed with the name of the project
    '''
    os.environ[PROJECT_NAME.upper() + "_" + name.upper()] = value


class Context(object):
    def __init__(self):
        self._project_path = PROJECT_LOCATION
        self._tmp_path = os.path.join(os.getcwd(), '.tmp')
        self._provider = None
        self._debug = False
        self._vagrant = True

        # env vars used by Python and Ruby
        set_env_var('env', self._project_path)
        set_env_var('tmp', self._tmp_path)

        if self._vagrant:
            # Vagrant requires the following 2 env vars for custom cwd and dotfile path.
            if 'VAGRANT_CWD' not in os.environ: # Where the Vagrantfile and python code are
                os.environ['VAGRANT_CWD'] = self._project_path # (default installed path)
            if 'VAGRANT_DOTFILE_PATH' not in os.environ: # Where to put .vagrant dir (right next to .tmp)
                os.environ['VAGRANT_DOTFILE_PATH'] = os.path.normpath(os.path.join(os.getcwd() + '/.vagrant')) # (default cwd)


pass_context = click.make_pass_decorator(Context, ensure=True)


@click.group()
@click.option('--debug/--no-debug', default=False)
@pass_context
def cli(ctx, debug):
    if debug:
        ctx._debug = debug

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
    if provider is not None:
        set_env_var('provider', provider)
    if provider not in PROVIDERS and provider is not None:
        # TODO See if there's a better exit / error system
        sys.exit('ABORTED - Target provider "%s" is not in the providers '
                 'list. Did you have a typo?' % provider)
    vagrant_up()

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

main = cli
