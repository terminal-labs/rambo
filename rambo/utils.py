import os

from pathlib import Path
from shutil import copyfile, move, rmtree

def dir_exists(path):
    return os.path.isdir(path)

def dir_create(path):
    if not os.path.exists(path):
        os.makedirs(path)

def dir_delete(path):
    rmtree(path)

def file_delete(path):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass

def file_copy(src, dst):
    copyfile(src, dst)

def file_rename(src, dst):
    os.rename(src, dst)

def file_move(src, dst):
    move(src, dst)

def get_user_home():
    return str(Path.home())
