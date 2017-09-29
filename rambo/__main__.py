import sys

import click
from bash import bash

from rambo.app import setup_rambo, setup_lastpass, vagrant_up, vagrant_ssh, vagrant_destroy

tool_name = 'rambo'

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
@click.pass_context
def gen(ctx):
    print("warning -- you entered a command " + tool_name  + " does not understand. passing raw commands to vagrant backend")
    print('you ran "', ' '.join(list(sys.argv)),'"')
    print('vagrant backend says:')
    print(bash('cd .rambo; vagrant ' + sys.argv[1]).stdout)

@cli.command()
@click.pass_context
def up(ctx):
    vagrant_up()

@cli.command()
@click.pass_context
def ssh(ctx):
    vagrant_ssh()

@cli.command()
@click.pass_context
def destroy(ctx):
    vagrant_destroy()

@cli.command()
@click.pass_context
def setup(ctx):
    setup_rambo()
    setup_lastpass()

def main():
    cli(obj={})

if __name__ == '__main__':
    main()
