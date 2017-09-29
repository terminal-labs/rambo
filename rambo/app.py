import os
import time
from threading import Thread

import click
from bash import bash

from rambo.utils import get_user_home, dir_exists, dir_create, dir_delete, file_copy, file_delete, file_rename
from rambo.scripts import install_script, install_lastpass

# Progressively read a file as it's being written to by another function, i.e. Vagrant.
def follow_log_file(log_file_path, exit_triggers):
    file_obj = open(log_file_path, 'r')
    while 1:
        where = file_obj.tell()
        line = file_obj.readline()
        if not line:
            time.sleep(0.1)
            file_obj.seek(where)
        else:
            click.echo(line.strip()) # Strip trailing eol.
            if any(string in line for string in exit_triggers):
                break


def vagrant_up_thread():
    dir_create('.tmp/logs')
    bash('vagrant up > .tmp/logs/vagrant-up-log')

def vagrant_up():
    if not dir_exists('.tmp'):
        dir_create('.tmp')
    dir_create('.tmp/logs')
    open('.tmp/logs/vagrant-up-log','w').close() # Create log file. Vagrant will write to it, we'll read it.
    thread = Thread(target = vagrant_up_thread) # Threaded to write, read, and echo as `up` progresses.
    thread.start()
    # TODO concat and cycle logs.
    follow_log_file('.tmp/logs/vagrant-up-log', ['default: Total run time:'])
    click.echo('Up complete.')

def vagrant_ssh():
    os.system('vagrant ssh')

def vagrant_destroy(): # TODO add an --all flag to delete the whole .tmp dir. Default leaves logs.
    dir_create('.tmp/logs')
     # TODO concat and cycle logs.
    bash('vagrant destroy --force > .tmp/logs/vagrant-destroy-log')
    follow_log_file('.tmp/logs/vagrant-destroy-log', ['Vagrant done with destroy.'])
    file_delete('.tmp/provider')
    file_delete('.tmp/random_tag')
    dir_delete('.vagrant')
    click.echo('Temporary files removed')
    click.echo('Destroy complete.')

def setup_lastpass_thread():
    dir_create(get_user_home() + '/.tmp-common')
    with open(get_user_home() + '/.tmp-common/install-lastpass.sh', 'w') as file_obj:
        file_obj.write(install_lastpass)
    bash('cd ' + get_user_home() + '/.tmp-common; bash install-lastpass.sh > install-lastpass-log')
    with open(get_user_home() + '/.tmp-common/install-lastpass-log', 'a') as file_obj:
        file_obj.write('done installing lastpass')

def setup_lastpass():
    dir_create(get_user_home() + '/.tmp-common')
    open(get_user_home() + '/.tmp-common/install-lastpass-log','w')
    thread = Thread(target = setup_lastpass_thread)
    thread.start()
    follow_log_file(get_user_home() + '/.tmp-common/install-lastpass-log', ['one installing lastpass'])
