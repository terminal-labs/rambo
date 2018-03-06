import click
import distutils
import errno
import json
import os
import pty
import shutil
import subprocess
import sys
import time
import platform
from distutils.dir_util import copy_tree
from distutils.errors import DistutilsFileError
from select import select
from subprocess import Popen
from threading import Thread

import rambo.providers as providers
import rambo.utils as utils
from rambo.scripts import install_lastpass
from rambo.settings import SETTINGS, PROJECT_LOCATION, PROJECT_NAME
from rambo.utils import get_env_var, set_env_var


def write_to_log(data=None, file_name=None):
    '''Write data to log files. Will append data to a single combined log.
    Additionally write data to a log with a custom name (such as stderr)
    for any custom logs.

    Args:
        data (str or bytes): Data to write to log file.
        file_name (str): Used to create (or append to) an additional
                         log file with a custom name. Custom name always gets
                         `.log` added to the end.
    '''
    try:
        data = data.decode('utf-8')
    except AttributeError:
        pass # already a string

    data = ''.join([data.rstrip(), '\n']) # strip possible eol chars and add back exactly one

    utils.dir_create(get_env_var('LOG_PATH'))
    fd_path = os.path.join(get_env_var('LOG_PATH'), 'history.log')
    fd = open(fd_path, 'a+')
    fd.write(data)
    fd.close()
    if file_name:
        fd_custom_path = os.path.join(get_env_var('LOG_PATH'), ''.join([file_name, '.log']))
        fd_custom = open(fd_custom_path, 'a+')
        fd_custom.write(data)
        fd_custom.close()

def _invoke_vagrant(cmd=None):
    '''Pass a command to vagrant. This outputs in near real-time,
    logs both stderr and stdout in a combined file, and detects stderr for
    our own error handling.

    Returns returncode (exitcode) of the command.

    Args:
        cmd (str): The cmd string that is appended to `vagrant ...`,
                   passed to the shell and executed.
    '''
    masters, slaves = zip(pty.openpty(), pty.openpty())
    cmd = ' '.join(['vagrant', cmd]).split()

    with Popen(cmd, stdin=slaves[0], stdout=slaves[0], stderr=slaves[1]) as p:
        for fd in slaves:
            os.close(fd) # no input
            readable = {
                masters[0]: sys.stdout.buffer, # store buffers seperately
                masters[1]: sys.stderr.buffer,
            }
        while readable:
            for fd in select(readable, [], [])[0]:
                try:
                    data = os.read(fd, 1024) # read available
                except OSError as e:
                    if e.errno != errno.EIO:
                        raise #XXX cleanup
                    del readable[fd] # EIO means EOF on some systems
                else:
                    if not data: # EOF
                        del readable[fd]
                    else:
                        if fd == masters[0]: # We caught stdout
                            click.echo(data.rstrip())
                            write_to_log(data)
                        else: # We caught stderr
                            click.echo(data.rstrip(), err=True)
                            write_to_log(data, 'stderr')
                        readable[fd].flush()
    for fd in masters:
        os.close(fd)
    return p.returncode

## Defs used by main cli cmd
def set_init_vars(cwd=None, tmpdir_path=None):
    '''Set custom environment variables that are always going to be needed by
    our custom Ruby code in the Vagrantfile chain.

    Args:
        cwd (path): Location of project (conf file, provisioning scripts, etc.).
        tmpdir_path (path): Location of project's tmp dir.
    '''
    # env vars available to Python and Ruby
    set_env_var('ENV', PROJECT_LOCATION) # installed location of this code

    # effective CWD (likely real CWD, but may be changed by user.
    if cwd: # cli / api
        set_env_var('CWD', cwd)
    elif not get_env_var('CWD'): # Not previously set env var either
        try:
            set_env_var('CWD', os.getcwd())
        except FileNotFoundError:
            utils.abort('Your current working directory no longer exists. '
                  'Did you delete it? Check for it with `ls ..`')

    # loc of tmpdir_path
    if tmpdir_path: # cli / api
        set_env_var('TMPDIR_PATH',
                    os.path.join(tmpdir_path, '.%s-tmp' % PROJECT_NAME))
    elif get_env_var('TMPDIR_PATH'): # Previously set env var
        set_env_var('TMPDIR_PATH',
                    os.path.join(get_env_var('TMPDIR_PATH'),
                                 '.%s-tmp' % PROJECT_NAME))
    else: # Not set, set to default loc
        set_env_var('TMPDIR_PATH',
                    os.path.join(os.getcwd(),
                                 '.%s-tmp' % PROJECT_NAME)) # default (cwd)
    set_env_var('LOG_PATH', os.path.join(get_env_var('TMPDIR_PATH'), 'logs'))

def set_vagrant_vars(vagrant_cwd=None, vagrant_dotfile_path=None):
    '''Set the environment varialbes prefixed with `VAGRANT_` that vagrant
    expects, and that we use, to modify some use paths.

    Agrs:
        vagrant_cwd (path): Location of `Vagrantfile`. Used if invoked with API only.
        vagrant_dotfile_path (path): Location of `.vagrant` metadata directory. Used if invoked with API only.
    '''
    # loc of Vagrantfile
    if vagrant_cwd: # cli / api
        os.environ["VAGRANT_CWD"] = vagrant_cwd
    elif 'VAGRANT_CWD' not in os.environ: # Not set in env var
        # if custom Vagrantfile exists in the default location.
        if os.path.isfile(os.path.join(os.getcwd(), 'Vagrantfile')):
            os.environ['VAGRANT_CWD'] = os.getcwd()
        else: # use default (installed) path
            os.environ['VAGRANT_CWD'] = PROJECT_LOCATION
    # loc of .vagrant dir
    if vagrant_dotfile_path: # cli / api
        os.environ['VAGRANT_DOTFILE_PATH'] = vagrant_dotfile_path
    elif 'VAGRANT_DOTFILE_PATH' not in os.environ: # Not set in env var
        os.environ['VAGRANT_DOTFILE_PATH'] = os.path.normpath(os.path.join(os.getcwd(), '.vagrant')) # default (cwd)

## Defs for cli subcommands
def createproject(project_name, config_only=None):
    '''Create project with basic configuration files.

    Agrs:
        project_name (path): Place to create a new project. Must be non-existing dir.
        config_only (bool): Determins if we should only place a conf file in the new project.
    '''
    ## Create project dir
    path = os.path.join(os.getcwd(), project_name)
    try:
        os.makedirs(path) # Make parent dirs if needed.
    except FileExistsError:
        utils.abort('Directory already exists.')
    click.echo('Created %s project "%s" in %s.'
               % (PROJECT_NAME.capitalize(), project_name, path))
    ## Fill project dir with basic configs.
    install_config(output_path=path)
    if not config_only:
        export('saltstack', path)
        install_auth(output_path=path)

def destroy(ctx=None, vagrant_cwd=None, vagrant_dotfile_path=None):
    '''Destroy a VM / container and all its metadata. Default leaves logs.
    All str args can also be set as an environment variable; arg takes precedence.

    Agrs:
        ctx (object): Click Context object.
        vagrant_cwd (path): Location of `Vagrantfile`. Used if invoked with API only.
        vagrant_dotfile_path (path): Location of `.vagrant` metadata directory. Used if invoked with API only.
    '''
    # TODO add finding and deleting of all VMs registered to this installation.
    # TODO (optional) add finding and deleting of all VMs across all installations.
    # TODO add an --all flag to delete the whole .rambo-tmp dir. Default leaves logs.

    if not ctx: # Using API. Else handled by cli.
        set_init_vars()
        set_vagrant_vars(vagrant_cwd, vagrant_dotfile_path)

    vagrant_general_command('destroy --force')
    utils.file_delete(os.path.join(get_env_var('TMPDIR_PATH'), '/provider'))
    utils.file_delete(os.path.join(get_env_var('TMPDIR_PATH'), '/random_tag'))
    utils.dir_delete(os.environ.get('VAGRANT_DOTFILE_PATH'))
    click.echo('Temporary files removed')
    click.echo('Destroy complete.')

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
            distutils.dir_util.copy_tree(src, dst) # Merge copy tree with overwrites.
        except DistutilsFileError: # It's a file, not a dir.
            try:
                shutil.copy(src, dst) # Copy file with overwrites.
            except FileNotFoundError:
                os.makedirs(os.path.dirname(dst), exist_ok=True) # Make parent dirs if needed. # Py 3.2+
                shutil.copy(src, dst) # Copy file with overwrites.

    click.echo('Done exporting %s code.' % resource)

def install_auth(ctx=None, output_path=None):
    '''Install auth directory.

    Agrs:
        ctx (object): Click Context object.
        output_path (path): Path to place auth dir.
    '''
    if not ctx: # Using API. Else handled by cli.
        set_init_vars()

    if not output_path:
        output_path = get_env_var('cwd')
    license_dir = os.path.join(output_path, 'auth/licenses')
    try:
        os.makedirs(license_dir)
    except FileExistsError:
        pass # Dir already created. Moving on.
    click.echo('Any (license) files you put in %s will be synced into your VM.'
               % license_dir)

    for filename in os.listdir(os.path.join(get_env_var('env'), 'auth/env_scripts')):
        dst_dir = os.path.join(output_path, 'auth/keys')
        dst = os.path.join(dst_dir, os.path.splitext(filename)[0])
        if not os.path.isfile(dst):
            os.makedirs(dst_dir, exist_ok=True) # Make parent dirs if needed. # Py 3.2+
            shutil.copy(os.path.join(get_env_var('env'), 'auth/env_scripts', filename), dst)
            click.echo('Added template key loading scripts %s to auth/keys.' % filename)
        else:
            click.echo('File %s exists. Leaving it.' % dst)

    # TODO: Have Rambo optionally store the same keys that may be in auth/keys in metadata,
    # added from the cli/api. Automatically check if keys in metatdata and not keys
    # in env vars, and set them. This is an avenue for expanding the cli/api's use
    # and not needing the auth key scripts.
    # load_provider_keys()

def install_config(ctx=None, output_path=None):
    '''Install config file.

    Agrs:
        ctx (object): Click Context object.
        output_path (path): Path to place conf file.
    '''
    if not ctx: # Using API. Else handled by cli.
        set_init_vars()

    if not output_path:
        output_path = get_env_var('cwd')
    path = os.path.join(output_path, '%s.conf' % PROJECT_NAME)

    if os.path.exists(path):
        utils.abort('%s.conf already esists.' % PROJECT_NAME)
    else:
        with open(path, 'w') as f:
            f.write('[up]\nprovider = %s\nguest_os = %s\n'
                    % (SETTINGS['PROVIDERS_DEFAULT'], SETTINGS['GUEST_OSES_DEFAULT']))
        click.echo('Created config at %s' % path)

def install_plugins(force=None, plugins=('all',)):
    '''Install all of the vagrant plugins needed for all plugins

    Agrs:
        force (bool): Forces bypassing of reinstallation prompt.
        plugins (tuple): Names of vagrant plugins to install.
    '''
    host_system = platform.system()
    for plugin in plugins:
        if plugin == 'all':
            click.echo('Installing all default plugins.')
            for plugin in SETTINGS['PLUGINS'][host_system]:
                _invoke_vagrant('plugin install %s' % plugin)
        elif plugin in SETTINGS['PLUGINS'][host_system]:
            _invoke_vagrant('plugin install %s' % plugin)
        else:
            if not force:
                click.confirm('The plugin "%s" is not in our list of plugins. Attempt '
                          'to install anyway?' % plugin, abort=True)
            vagrant_general_command('plugin install %s' % plugin)

def scp(ctx=None, locations=None):
    '''Transfer file or dir with scp. This makes use of the vagrant-scp plugin,
    which allows for simplified args.
    '''
    if len(locations)!=2:
        utils.abort("There needs to be exactly two arguments for scp, a 'from' location "
                    "and a 'to' location.\nYou gave: %s." % ' '.join(locations))

    copy_from = locations[0]
    copy_to = locations[1]

    if ':' in copy_from: # copy_from is remote, fix copy_to which is local
        copy_to = os.path.abspath(copy_to)
    else: # if no ':' in copy_from, copy_to must be remote, fix copy_from which is local
        copy_from = os.path.abspath(copy_from)

    locations = [copy_from, copy_to]

    vagrant_general_command('{} {}'.format('scp', ' '.join(locations)))

def ssh(ctx=None, command=None, vagrant_cwd=None, vagrant_dotfile_path=None):
    '''Connect to an running VM / container over ssh.
    All str args can also be set as an environment variable; arg takes precedence.

    Agrs:
        ctx (object): Click Context object.
        command (str): Pass-through command to run with `vagrant ssh --command`.
        vagrant_cwd (path): Location of `Vagrantfile`. Used if invoked with API only.
        vagrant_dotfile_path (path): Location of `.vagrant` metadata directory. Used if invoked with API only.
    '''
    # TODO: Better logs.
    if not ctx: # Using API. Else handled by cli.
        set_init_vars()
        set_vagrant_vars(vagrant_cwd, vagrant_dotfile_path)

    ## Add pass-through 'command' option.
    cmd = 'vagrant ssh'
    if command:
        cmd = ' '.join([cmd, '--command', command])

    # do not use _invoke_vagrant, that will give a persistent ssh session regardless.
    os.system(cmd)

def up(ctx=None, provider=None,  guest_os=None, ram_size=None, drive_size=None,
       machine_type=None, provision=None, destroy_on_error=None,
       vagrant_cwd=None, vagrant_dotfile_path=None):
    '''Start a VM / container with `vagrant up`.
    All str args can also be set as an environment variable; arg takes precedence.

    Agrs:
        ctx (object): Click Context object. Used to detect if CLI is used.
        provider (str): Provider to use.
        guest_os (str): Guest OS to use.
        ram_size (int): RAM in MB to use.
        drive_size (int): Drive size in GB to use.
        machine_type (str): Machine type to use for cloud providers.
        provision (bool): vagrant provisioning flag.
        destroy_on_error (bool): vagrant destroy-on-error flag.
        vagrant_cwd (path): Location of `Vagrantfile`. Used if invoked with API only.
        vagrant_dotfile_path (path): Location of `.vagrant` metadata directory. Used if invoked with API only.
    '''
    # TODO: Add registering of VM for all of this installation to see

    if not ctx: # Using API. Else handled by cli.
        set_init_vars()
        set_vagrant_vars(vagrant_cwd, vagrant_dotfile_path)

    ## provider. Make this be last.
    if not provider:
        provider = SETTINGS['PROVIDERS_DEFAULT']
    set_env_var('provider', provider)

    if provider not in SETTINGS['PROVIDERS']:
        msg = ('Provider "%s" is not in the provider list.\n'
               'Did you have a typo? Here is as list of avalible providers:\n\n'
               % provider)
        for supported_provider in SETTINGS['PROVIDERS']:
            msg = msg + '%s\n' % supported_provider
        utils.abort(msg)

    ## guest_os
    if not guest_os:
        guest_os = SETTINGS['GUEST_OSES_DEFAULT']
    set_env_var('guest_os', str(guest_os))

    if guest_os not in SETTINGS['GUEST_OSES']:
        msg = ('Guest OS "%s" is not in the guest OSes whitelist.\n'
               'Did you have a typo? We\'ll try anyway.\n'
               'Here is as list of avalible guest OSes:\n\n'
               % guest_os)
        for supported_os in SETTINGS['GUEST_OSES']:
            msg = msg + '%s\n' % supported_os
        utils.warn(msg)

    ## ram_size and drive_size (coupled)
    # Cast to strings if they exist so they can stored as env vars.
    if ram_size:
        ram_size = str(ram_size)
    if drive_size:
        drive_size = str(drive_size)

    if ram_size and not drive_size:
        try:
            drive_size = SETTINGS['SIZES'][ram_size]
        except KeyError: # Doesn't match, but we'll let them try it.
            drive_size = SETTINGS['DRIVESIZE_DEFAULT']
    elif drive_size and not ram_size:
        try:
            ram_size = list(SETTINGS['SIZES'].keys())[list(SETTINGS['SIZES'].values()).index(drive_size)]
        except ValueError: # Doesn't match, but we'll let them try it.
            ram_size = SETTINGS['RAMSIZE_DEFAULT']
    elif not ram_size and not drive_size:
        ram_size = SETTINGS['RAMSIZE_DEFAULT']
        drive_size = SETTINGS['DRIVESIZE_DEFAULT']
    # else both exist, just try using them

    set_env_var('ramsize', ram_size)
    set_env_var('drivesize', drive_size)

    ## ram_size
    if ram_size not in iter(SETTINGS['SIZES']):
        msg = ('RAM Size "%s" is not in the RAM sizes list.\n'
               'Did you have a typo? We\'ll try anyway.\n'
               'Here is as list of avalible RAM sizes:\n\n'
               % ram_size)
        for supported_ram_size in iter(SETTINGS['SIZES']):
            msg = msg + '%s\n' % supported_ram_size
        utils.warn(msg)

    ## drive_size
    if drive_size not in iter(SETTINGS['SIZES'].values()):
        msg = ('DRIVE Size "%s" is not in the DRIVE sizes list.\n'
               'Did you have a typo? We\'ll try anyway.\n'
               'Here is as list of avalible DRIVE sizes:\n\n'
               % drive_size)
        for supported_drive_size in iter(SETTINGS['SIZES'].values()):
            msg = msg + '%s\n' % supported_drive_size
        utils.warn(msg)

    if machine_type:
        if provider in ('docker', 'lxc', 'virtualbox'):
            msg = ('You have selected a machine-type, but are not using\n'
                   'a cloud provider. You selected %s with %s.\n'
                   % (machine_type, provider))
            utils.abort(msg)
        set_env_var('machinetype', machine_type)


    ## Provider specific handling.
    ## Must come after all else, because logic may be done on env vars set above.
    if provider == 'digitalocean':
        providers.digitalocean()
    elif provider == 'docker':
        providers.docker()
    elif provider == 'ec2':
        providers.ec2()


    ## Add straight pass-through flags. Keep test for True/False explicit as only those values should work
    cmd = 'up'
    if provision is True:
        cmd = '{} {}'.format(cmd, '--provision')
    elif provision is False:
        cmd = '{} {}'.format(cmd, '--no-provision')

    if destroy_on_error is True:
        cmd = '{} {}'.format(cmd, '--destroy-on-error')
    elif destroy_on_error is False:
        cmd = '{} {}'.format(cmd, '--no-destroy-on-error')

    vagrant_general_command(cmd)

def vagrant_general_command(cmd):
    '''Invoke vagrant with custom command.

    Args:
        cmd (str): String to append to command `vagrant ...`
    '''
    # Modify cmd in private function to keep enforcement of being a vagrant cmd there.
    _invoke_vagrant(cmd)

## Unused defs
def setup_lastpass():
    utils.dir_create(os.path.join(utils.get_user_home(), '/.tmp-common'))
    open(os.path.join(utils.get_user_home(), '/.tmp-common/install-lastpass-log'),'w')
    utils.dir_create(os.path.join(utils.get_user_home(), '/.tmp-common'))
    with open(os.path.join(utils.get_user_home(), '/.tmp-common/install-lastpass.sh'), 'w') as file_obj:
        file_obj.write(install_lastpass)
    # Not used, and won't work as is because we're now enforcing use of vagrant in private function.
    vagrant_general_command(os.path.join('cd ', utils.get_user_home(), '/.tmp-common; bash install-lastpass.sh'), ' install-lastpass-log')


class Run_app():
    def __init__(self):
        print("in Run_app __init__")
