import os
import sys
import json
import ipdb
import click
from bash import bash

from rambo.utils import set_env_var
from rambo.app import vagrant_up, vagrant_ssh, vagrant_destroy

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

class Context(object):
    def __init__(self):
        self.project_path = PROJECT_LOCATION
        self._tmp_path = os.path.join(os.getcwd(), '.tmp')
        self._provider = None
        self.debug = False
        self.vagrant_cwd = None
        self.vagrant_dotfile_path = None

        # env vars used by Python and Ruby
        set_env_var('env', self.project_path)
        set_env_var('tmp', self._tmp_path)

        ## Vagrant requires the following env vars for custom cwd and dotfile path. Keep if already set.
        # Where the Vagrantfile is located
        if 'VAGRANT_CWD' not in os.environ:
            os.environ['VAGRANT_CWD'] = self.project_path # (default installed path)
        # Where to put .vagrant dir and .tmp dirs
        if 'VAGRANT_DOTFILE_PATH' not in os.environ:
            os.environ['VAGRANT_DOTFILE_PATH'] = os.path.normpath(os.path.join(os.getcwd() + '/.vagrant')) # (default cwd)


pass_context = click.make_pass_decorator(Context, ensure=True)


@click.group()
@click.option('--debug/--no-debug', default=False,
              help='Debug option not yet implemented.')
@click.option('--vagrant-cwd', default=None, type=click.Path(),
              help='Path entry point to the Vagrantfile. Defaults to '
              'the Vagrantfile provided by %s in the installed path.'
              % PROJECT_NAME.capitalize())
@click.option('--vagrant-dotfile-path', default=None, type=click.Path(),
              help='Path location of the .vagrant directory for the '
              'virtual machine. Defaults to the current working directory.')
@pass_context
def cli(ctx, debug, vagrant_cwd, vagrant_dotfile_path):
    if debug:
        ctx.debug = debug

    # Overwrite Vagrant env vars if cli option is passed.
    if vagrant_cwd:
        os.environ['VAGRANT_CWD'] = os.path.normpath(vagrant_cwd) #os.environ['VAGRANT_CWD'] = 
    if vagrant_dotfile_path:
        os.environ['VAGRANT_DOTFILE_PATH'] = os.path.normpath(os.path.join(vagrant_dotfile_path + '/.vagrant'))
#    ipdb.set_trace()

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
@pass_context
def up(ctx, provider):
    '''Call Vagrant up with provider option. Provider may also be supplied by
    the RAMBO_PROVIDER environment variable if not passed as a cli option.
    '''
    ipdb.set_trace()
    vagrant_up(ctx, provider)

@cli.command()
def ssh():
    '''Connect to an running virtual machine over ssh.
    '''
    vagrant_ssh()

@cli.command()
def destroy():
    '''Destroy a virtual machine and all its metadata. Default leaves logs.
    '''
    vagrant_destroy()

@cli.command()
def setup(): # threaded setup commands
    '''Runs any setup commands. None yet implemented.
    '''
    # setup_rambo()
    setup_lastpass()

main = cli
