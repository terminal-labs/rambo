import errno
import os
import platform
import pty
import shutil
import sys
from distutils.dir_util import copy_tree
from distutils.errors import DistutilsFileError
from select import select
from subprocess import Popen

import click

import rambo.options as options
import rambo.utils as utils
from rambo.settings import SETTINGS, PROJECT_LOCATION, PROJECT_NAME
from rambo.utils import get_env_var, set_env_var, set_env, set_tmpdir, set_cwd, set_init_vars

def install_auth(ctx=None, output_path=None, **kwargs):
    '''Install auth directory.
    Agrs:
        ctx (object): Click Context object.
        output_path (path): Path to place auth dir.
    '''
    if not ctx: # Using API. Else handled by cli.
        set_init_vars(params.get('cwd'), params.get('tmpdir'))

    if not output_path:
        output_path = get_env_var('cwd')
    license_dir = os.path.join(output_path, 'auth/licenses')
    try:
        os.makedirs(license_dir)
    except FileExistsError:
        pass # Dir already created. Moving on.
    utils.echo('Any (license) files you put in %s will be synced into your VM.'
               % license_dir)

    for filename in os.listdir(os.path.join(get_env_var('env'), 'auth/env_scripts')):
        dst_dir = os.path.join(output_path, 'auth/keys')
        dst = os.path.join(dst_dir, os.path.splitext(filename)[0])
        if not os.path.isfile(dst):
            os.makedirs(dst_dir, exist_ok=True) # Make parent dirs if needed. # Py 3.2+
            shutil.copy(os.path.join(get_env_var('env'), 'auth/env_scripts', filename), dst)
            utils.echo('Added template key loading scripts %s to auth/keys.' % filename)
        else:
            utils.echo('File %s exists. Leaving it.' % dst)

    # TODO: Have Rambo optionally store the same keys that may be in auth/keys in metadata,
    # added from the cli/api. Automatically check if keys in metatdata and not keys
    # in env vars, and set them. This is an avenue for expanding the cli/api's use
    # and not needing the auth key scripts.
    # load_provider_keys()


def install_config(ctx=None, output_path=None, **kwargs):
    '''Install config file.
    Agrs:
        ctx (object): Click Context object.
        output_path (path): Path to place conf file.
    '''
    if not ctx: # Using API. Else handled by cli.
        set_init_vars(params.get('cwd'), params.get('tmpdir'))

    if not output_path:
        output_path = get_env_var('cwd')
    path = os.path.join(output_path, '%s.conf' % PROJECT_NAME)

    if os.path.exists(path):
        utils.abort('%s.conf already esists.' % PROJECT_NAME)
    else:
        with open(path, 'w') as f:
            f.write('[up]\nprovider = %s\nguest_os = %s\n'
                    % (SETTINGS['PROVIDERS_DEFAULT'], SETTINGS['GUEST_OSES_DEFAULT']))
        utils.echo('Created config at %s' % path)


def export(resource=None, export_path=None, force=None):
    '''Drop default code in the CWD / user defined space. Operate on saltstack
    and vagrant resources.
    Agrs:
        resource (str): Resource to export: saltstack or vagrant.
        export_path (path): Dir to export resources to.
        force (bool): Determins if we should overwrite and merge conflicting files in the target path.
    '''
    if export_path:
        output_dir = os.path.normpath(export_path)
    else:
        output_dir = os.getcwd()

    if resource in ('vagrant', 'saltstack'):
        srcs = [os.path.normpath(os.path.join(PROJECT_LOCATION, resource))]
        dsts = [os.path.join(output_dir, resource)]

    if resource == 'vagrant':
        srcs.append(os.path.normpath(os.path.join(PROJECT_LOCATION, 'settings.json')))
        srcs.append(os.path.normpath(os.path.join(PROJECT_LOCATION, 'Vagrantfile')))
        dsts.append(os.path.join(output_dir, 'settings.json'))
        dsts.append(os.path.join(output_dir, 'Vagrantfile'))

    if not force:
        try:
            for path in dsts:
                if os.path.exists(path):
                    click.confirm("One or more destination files or directories in "
                                  "'%s' already exists. Attempt to merge and "
                                  "overwrite?" % dsts, abort=True)
                    break # We only need general confirmation of an overwrite once.
        except UnboundLocalError: # dsts referenced before assignement
            utils.abort("The resource '%s' is not a valid option." % resource)

    for src, dst in zip(srcs, dsts):
        try:
            copy_tree(src, dst) # Merge copy tree with overwrites.
        except DistutilsFileError: # It's a file, not a dir.
            try:
                shutil.copy(src, dst) # Copy file with overwrites.
            except FileNotFoundError:
                os.makedirs(os.path.dirname(dst), exist_ok=True) # Make parent dirs if needed. # Py 3.2+
                shutil.copy(src, dst) # Copy file with overwrites.

    utils.echo('Done exporting %s code.' % resource)
