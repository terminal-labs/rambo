import os
import time

from threading import Thread

from bash import bash

from rambo.utils import get_user_home, dir_exists, dir_create, dir_delete, file_copy, file_delete, file_rename
from rambo.scripts import install_script, install_lastpass

def follow_log_file(log_file_path, exit_triggers):
    file_obj = open(log_file_path, 'r')
    while 1:
        where = file_obj.tell()
        line = file_obj.readline()
        if not line:
            time.sleep(0.1)
            file_obj.seek(where)
        else:
            if any(string in line for string in exit_triggers):
                break
            print(line)

def clone_rambo_repo_thread():
    bash('git clone --progress git@github.com:terminal-labs/rambo.git .rambo 2> .rambo-clone-log')

def vagrant_up_thread():
    dir_create('.rambo/.logs')
    bash('cd .rambo; vagrant up > .logs/vagrant-up-log')

def clone_rambo_repo():
    open('.rambo-clone-log','w')
    thread = Thread(target = clone_rambo_repo_thread)
    thread.start()
    follow_log_file('.rambo-clone-log', ['Checking connectivity','fatal: destination path'])

def vagrant_up():
    dir_create(get_user_home() + '/.rambo-common')
    if not dir_exists('.rambo'):
        clone_rambo_repo()
    dir_create('.rambo/.logs')
    open('.rambo/.logs/vagrant-up-log','w')
    thread = Thread(target = vagrant_up_thread)
    thread.start()
    follow_log_file('.rambo/.logs/vagrant-up-log', ['default: Total run time:'])

def vagrant_ssh():
    os.system('cd .rambo; vagrant ssh')

def vagrant_destroy():
    dir_create('.rambo/.logs')
    file_rename('.rambo/Vagrantfile', '.rambo/.Vagrantfile.old')
    file_copy('.rambo/vagrant_resources/base_vagrantfiles/Vagrantfile.virtualbox.basic', '.rambo/Vagrantfile')
    bash('cd .rambo; vagrant destroy --force > .logs/vagrant-destroy-log')
    file_delete('.rambo/Vagrantfile')
    file_rename('.rambo/.Vagrantfile.old', '.rambo/Vagrantfile')
    dir_delete('.rambo/.vagrant')
    dir_delete('.rambo/.logs')
    dir_delete('.rambo/.tmp')
    dir_delete('.rambo')

def setup_rambo_thread():
    dir_create(get_user_home() + '/.rambo-common')
    with open(get_user_home() + '/.rambo-common/install.sh', 'w') as file_obj:
        file_obj.write(install_script)
    bash('cd ' + get_user_home() + '/.rambo-common; sudo bash install.sh > install-log')
    with open(get_user_home() + '/.rambo-common/install-log', 'a') as file_obj:
        file_obj.write('done installing deps that need root')

def setup_rambo():
    dir_create(get_user_home() + '/.rambo-common')
    open(get_user_home() + '/.rambo-common/install-log','w')
    thread = Thread(target = setup_rambo_thread)
    thread.start()
    follow_log_file(get_user_home() + '/.rambo-common/install-log', ['done installing deps that need root'])

def setup_lastpass_thread():
    dir_create(get_user_home() + '/.rambo-common')
    with open(get_user_home() + '/.rambo-common/install-lastpass.sh', 'w') as file_obj:
        file_obj.write(install_lastpass)
    bash('cd ' + get_user_home() + '/.rambo-common; bash install-lastpass.sh > install-lastpass-log')
    with open(get_user_home() + '/.rambo-common/install-lastpass-log', 'a') as file_obj:
        file_obj.write('done installing lastpass')

def setup_lastpass():
    dir_create(get_user_home() + '/.rambo-common')
    open(get_user_home() + '/.rambo-common/install-lastpass-log','w')
    thread = Thread(target = setup_lastpass_thread)
    thread.start()
    follow_log_file(get_user_home() + '/.rambo-common/install-lastpass-log', ['one installing lastpass'])
