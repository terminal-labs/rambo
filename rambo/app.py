import distutils
import errno
import os
import platform
import pty
import shutil
import subprocess
import sys
import time
from distutils.dir_util import copy_tree
from distutils.errors import DistutilsFileError
from select import select
from subprocess import Popen
from threading import Thread

import rambo.options as options
import rambo.utils as utils
from rambo.settings import SETTINGS, PROJECT_LOCATION, PROJECT_NAME

## Defs for cli subcommands
def createproject(project_name, config_only=None):
    """Create project with basic configuration files.

    Agrs:
        project_name (path): Place to create a new project. Must be non-existing dir.
        config_only (bool): Determins if we should only place a conf file in the new project.
    """
    ## Create project dir
    path = os.path.join(os.getcwd(), project_name)
    try:
        os.makedirs(path)  # Make parent dirs if needed.
    except FileExistsError:
        utils.abort("Directory already exists.")
    utils.echo(
        'Created %s project "%s" in %s.'
        % (PROJECT_NAME.capitalize(), project_name, path)
    )
    ## Fill project dir with basic configs.
    install_config(output_path=path)
    if not config_only:
        export("saltstack", path)
        install_auth(output_path=path)


def export(resource=None, export_path=None, force=None):
    """Drop default code in the CWD / user defined space. Operate on saltstack
    and vagrant resources.
    Agrs:
        resource (str): Resource to export: saltstack or vagrant.
        export_path (path): Dir to export resources to.
        force (bool): Determins if we should overwrite and merge conflicting files in the target path.
    """
    if export_path:
        output_dir = os.path.normpath(export_path)
    else:
        output_dir = os.getcwd()

    if resource in ("vagrant", "saltstack"):
        srcs = [os.path.normpath(os.path.join(PROJECT_LOCATION, resource))]
        dsts = [os.path.join(output_dir, resource)]

    if resource == "vagrant":
        srcs.append(os.path.normpath(os.path.join(PROJECT_LOCATION, "settings.json")))
        srcs.append(os.path.normpath(os.path.join(PROJECT_LOCATION, "Vagrantfile")))
        dsts.append(os.path.join(output_dir, "settings.json"))
        dsts.append(os.path.join(output_dir, "Vagrantfile"))

    if not force:
        try:
            for path in dsts:
                if os.path.exists(path):
                    click.confirm(
                        "One or more destination files or directories in "
                        "'%s' already exists. Attempt to merge and "
                        "overwrite?" % dsts,
                        abort=True,
                    )
                    break  # We only need general confirmation of an overwrite once.
        except UnboundLocalError:  # dsts referenced before assignement
            utils.abort("The resource '%s' is not a valid option." % resource)

    for src, dst in zip(srcs, dsts):
        try:
            distutils.dir_util.copy_tree(src, dst)  # Merge copy tree with overwrites.
        except DistutilsFileError:  # It's a file, not a dir.
            try:
                shutil.copy(src, dst)  # Copy file with overwrites.
            except FileNotFoundError:
                os.makedirs(
                    os.path.dirname(dst), exist_ok=True
                )  # Make parent dirs if needed. # Py 3.2+
                shutil.copy(src, dst)  # Copy file with overwrites.

    utils.echo("Done exporting %s code." % resource)


def destroy(ctx=None, **params):
    print("stub for destroy")


def halt(ctx=None, *args, **params):
    print("stub for halt")


def install_auth(ctx=None, output_path=None, **params):
    print("stub for auth")


def install_config(ctx=None, output_path=None, **params):
    path = os.path.join(output_path, "%s.conf" % PROJECT_NAME)
    with open(path, "w") as f:
        f.write(
            "[up]\nprovider = %s\nguest_os = %s\n"
            % (SETTINGS["PROVIDERS_DEFAULT"], SETTINGS["GUEST_OSES_DEFAULT"])
        )
    utils.echo("Created config at %s" % path)


def scp(ctx=None, locations=None, **params):
    print("stub for scp")


def ssh(ctx=None, command=None, **params):
    print("stub for ssh")


def up(ctx=None, **params):
    context = {"id": "1223456", "key": "abcdef"}
    utils.init()
    utils.delete_df_store_files()
    utils.get_sdk()
    utils.create_rambo_tmp_dir()
    print(utils.resolve_secrets())
    utils.render_salt_cloud_configs(context, params["provider"])
    metadata = {}
    metadata["params"] = params

    if params["provider"] == "virtualbox":
        if utils.vagrant_is_installed():
            print("vagrant is installed")
        else:
            print("vagrant is not installed")
        vagrant_box_metadata = utils.get_vagrant_box_metadata(
            SETTINGS["GUEST_OSES"][params["guest_os"]]["virtualbox"]
        )
        current_version = vagrant_box_metadata["current_version"]["version"]
        cached = utils.vagrant_box_is_cached(
            SETTINGS["GUEST_OSES"][params["guest_os"]]["virtualbox"], current_version
        )
        if cached:
            print("vagrant box is cached -- registering")
        else:
            print("vagrant box is not cached -- downloading")
            utils.get_vagrant_box(
                SETTINGS["GUEST_OSES"][params["guest_os"]]["virtualbox"],
                current_version,
            )

        metadata["vagrant_box_metadata"] = vagrant_box_metadata

    # print(params)
    # print(SETTINGS)
    # print(metadata)
    # print(utils.list_cached_vagrant_boxes())
    # print(utils.get_cached_vagrant_boxes_versions())
    # print(utils.vagrant_box_is_cached(SETTINGS["GUEST_OSES"][params["guest_os"]]["virtualbox"], current_version))

    utils.write_json_metadata_file(metadata)


class Run_app():

    def __init__(self):
        print("in Run_app __init__")
