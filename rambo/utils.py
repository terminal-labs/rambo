import json
import os
import sys
from pathlib import Path
from shutil import copyfile, move, rmtree

import re
import tempfile
import zipfile
import tarfile
import shutil
import hashlib

import click
import requests

from rambo.settings import PROJECT_NAME

VERSION='0.0.3.dev'
HOME = os.path.expanduser("~")
CWD = os.getcwd()
CHUNK_SIZE = 1024 * 32
RAMBO_HOME_DIR = ".rambo.d"
SLASH_ENCODING = "-VAGRANTSLASH-"
VAGRANT_API_URL = "https://app.vagrantup.com/api/v1/box/"
VAGRANT_APP_URL = "https://app.vagrantup.com/"
SDK_URL = "https://download.virtualbox.org/virtualbox/5.2.10/VirtualBoxSDK-5.2.10-122088.zip"

# https://app.vagrantup.com/terminal-labs/boxes/tl-ubuntu-1604-64bit-30gb/versions/0.2/providers/virtualbox.box

mock_var_dict = {}
mock_var_dict["RAMBO_TMPDIR_PATH"] = PROJECT_NAME + "-tmp"
mock_var_dict["RAMBO_LOG_PATH"] = os.path.join(
    mock_var_dict["RAMBO_TMPDIR_PATH"], "logs"
)


def abort(msg):
    msg = click.style("".join(["ABORTED - ", msg]), fg="red", bold=True)
    write_to_log(msg, "stderr")
    sys.exit(msg)


def echo(msg, err=None):
    if err:
        write_to_log(msg, "stderr")
        click.echo(msg, err=err)
    else:
        write_to_log(msg)
        click.echo(msg)


def warn(msg):
    msg = click.style("".join(["WARNING - ", msg]), fg="yellow")
    echo(msg)


def write_to_log(data=None, file_name=None):
    """Write data to log files. Will append data to a single combined log.
    Additionally write data to a log with a custom name (such as stderr)
    for any custom logs.

    Args:
        data (str or bytes): Data to write to log file.
        file_name (str): Used to create (or append to) an additional
                         log file with a custom name. Custom name always gets
                         `.log` added to the end.
    """
    try:
        data = data.decode("utf-8")
    except AttributeError:
        pass  # already a string

    # strip possible eol chars and add back exactly one
    data = "".join([data.rstrip(), "\n"])

    dir_create(os.path.join(mock_var_dict["RAMBO_TMPDIR_PATH"], "logs"))
    fd_path = os.path.join(mock_var_dict["RAMBO_TMPDIR_PATH"], "history.log")
    fd = open(fd_path, "a+")
    fd.write(data)
    fd.close()
    if file_name:
        fd_custom_path = os.path.join(
            mock_var_dict["RAMBO_TMPDIR_PATH"], "".join([file_name, ".log"])
        )
        fd_custom = open(fd_custom_path, "a+")
        fd_custom.write(data)
        fd_custom.close()


def create_rambo_tmp_dir():
    dir_create(os.path.join(CWD, "." + PROJECT_NAME + "-tmp"))


def write_json_metadata_file(data):
    create_rambo_tmp_dir()
    with open(
        os.path.join(CWD, "." + PROJECT_NAME + "-tmp", "metadata.json"), "w"
    ) as outfile:
        json.dump(data, outfile)


def get_vagrant_box_metadata(tag):
    r = requests.get(VAGRANT_API_URL + tag)
    return json.loads(r.text)


def list_cached_vagrant_boxes():
    directory = HOME + "/" + RAMBO_HOME_DIR + "/boxes"
    dirs = os.listdir(directory)
    dirs = [dir.replace(SLASH_ENCODING, "/") for dir in dirs]
    return dirs


def get_cached_vagrant_boxes_versions():
    dirs = list_cached_vagrant_boxes()

    dir_struct = {}

    for dir in dirs:
        directory = HOME + "/" + RAMBO_HOME_DIR + "/boxes" + "/" + dir.replace(
            "/", SLASH_ENCODING
        )
        versions = os.listdir(directory)
        dir_struct[dir] = versions
    return dir_struct


def vagrant_box_is_cached(tag, version):
    dir_struct = get_cached_vagrant_boxes_versions()
    if tag in dir_struct.keys() and version in dir_struct[tag]:
        return True
    else:
        return False


def download_file(url, local_filename):
    r = requests.get(url, stream=True)
    with open(local_filename, "wb") as f:
        for _ in r.iter_content(chunk_size=CHUNK_SIZE):
            if _:
                f.write(_)
    return local_filename


def uncompress_box_file(local_directory, file_path):
    try_unzip = True
    try_untar_gzip = False
    try_untar = False

    if try_unzip:
        try:
            zipfile.ZipFile(file_path).extractall(local_directory)
        except zipfile.error:
            try_untar = True
            try_untar_gzip = True

    if try_untar_gzip:
        tar = tarfile.open(file_path, "r:gz")
        tar.extractall(path=local_directory)
        tar.close()
        try_untar = False

    if try_untar:
        tar = tarfile.open(file_path, "r:")
        tar.extractall(path=local_directory)
        tar.close()


def check_integrity(local_directory):
    for _ in os.listdir(local_directory):
        if _.endswith(".mf"):
            with open(os.path.join(local_directory, _)) as file_obj:
                for _ in file_obj:
                    if _.count("=") > 0:
                        left_part = _.split("=")[0]
                        left_part = left_part.strip()
                        right_part = _.split("=")[1]
                        right_part = right_part.strip()
                        if "SHA256" in left_part:
                            hashtype = "SHA256"
                            hash_digest = right_part
                            file_path = os.path.join(
                                local_directory, left_part.split("(")[1].split(")")[0]
                            )
                            compare_hash(hashtype, hash_digest, file_path)


def sha256_checksum(filename, block_size=65536):
    sha256 = hashlib.sha256()
    with open(filename, "rb") as f:
        for block in iter(lambda: f.read(block_size), b""):
            sha256.update(block)
    return sha256.hexdigest()


def compare_hash(hashtype, hash_digest, file_path):
    print(hashtype, hash_digest, file_path)
    print(sha256_checksum(file_path))


def prepair_box_name(box_name):
    return box_name.replace("/", SLASH_ENCODING)


def resolve_vagrant_box_url(box_tag, box_version):
    box_url = VAGRANT_APP_URL + box_tag.split("/")[
        0
    ] + "/boxes/" + box_tag.split(
        "/"
    )[
        1
    ] + "/versions/" + box_version + "/providers/virtualbox.box"
    return box_url


def get_sdk():
    download_file(
        SDK_URL, os.path.join(HOME + "/" + RAMBO_HOME_DIR + "/vboxsdk", "sdk.zip")
    )
    zipfile.ZipFile(
        os.path.join(HOME + "/" + RAMBO_HOME_DIR + "/vboxsdk", "sdk.zip")
    ).extractall(
        HOME + "/" + RAMBO_HOME_DIR + "/vboxsdk"
    )


def get_vagrant_box(box_tag, box_version):
    box_name = box_tag
    box_name = prepair_box_name(box_name)

    box_url = resolve_vagrant_box_url(box_tag, box_version)
    box_filename = os.path.basename(box_url)

    directory = HOME + "/" + RAMBO_HOME_DIR + "/boxes" + "/" + box_name
    if not os.path.exists(directory):
        os.makedirs(directory)

    directory = HOME + "/" + RAMBO_HOME_DIR + "/raw_boxes" + "/" + box_name
    if not os.path.exists(directory):
        os.makedirs(directory)

    directory = HOME + "/" + RAMBO_HOME_DIR + "/boxes" + "/" + box_name + "/" + box_version
    if not os.path.exists(directory):
        os.makedirs(directory)

    with tempfile.TemporaryDirectory() as td_path:
        print(td_path)
        download_file(box_url, os.path.join(td_path, "box"))
        shutil.copy(
            os.path.join(td_path, "box"),
            HOME
            + "/"
            + RAMBO_HOME_DIR
            + "/raw_boxes"
            + "/"
            + box_name
            + "/"
            + box_filename,
        )
        uncompress_box_file(
            os.path.join(td_path, "contents"), os.path.join(td_path, "box")
        )
        shutil.copytree(
            os.path.join(td_path, "contents"),
            HOME
            + "/"
            + RAMBO_HOME_DIR
            + "/boxes"
            + "/"
            + box_name
            + "/"
            + box_version
            + "/virtualbox",
        )
        check_integrity(os.path.join(td_path, "contents"))


def init():
    directory = HOME + "/" + RAMBO_HOME_DIR
    if not os.path.exists(directory):
        os.makedirs(directory)

    directory = HOME + "/" + RAMBO_HOME_DIR + "/vboxsdk"
    if not os.path.exists(directory):
        os.makedirs(directory)

    directory = HOME + "/" + RAMBO_HOME_DIR + "/boxes"
    if not os.path.exists(directory):
        os.makedirs(directory)

    directory = HOME + "/" + RAMBO_HOME_DIR + "/raw_boxes"
    if not os.path.exists(directory):
        os.makedirs(directory)


def dir_exists(path):
    return os.path.isdir(path)


def dir_create(path):
    if not os.path.exists(path):
        os.makedirs(path)


def dir_delete(path):
    try:
        rmtree(path)
    except FileNotFoundError:
        pass


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
