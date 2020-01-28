import distutils
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
import rambo.vagrant_providers as vagrant_providers
from rambo.settings import SETTINGS, PROJECT_LOCATION, PROJECT_NAME
from rambo.utils import get_env_var, set_env_var


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
                            utils.echo(data.rstrip())
                            utils.write_to_log(data)
                        else: # We caught stderr
                            utils.echo(data.rstrip(), err=True)
                            utils.write_to_log(data, 'stderr')
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
    os.chdir(get_env_var('cwd'))

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
    utils.echo('Created %s project "%s" in %s.'
               % (PROJECT_NAME.capitalize(), project_name, path))
    ## Fill project dir with basic configs.
    install_config(output_path=path)
    if not config_only:
        export('saltstack', path)
        install_auth(output_path=path)

def destroy(ctx=None, **params):
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
        set_init_vars(params.get('cwd'), params.get('tmpdir_path'))
        set_vagrant_vars(params.get('vagrant_cwd'), params.get('vagrant_dotfile_path'))

    vagrant_general_command('destroy --force')
    if "vm_name" in params:
        utils.echo(f"Now removing base VirtualBox data for VM {params['vm_name']}.")
        os.system(f"vboxmanage controlvm {params['vm_name']} poweroff")
        os.system(f"vboxmanage unregistervm {params['vm_name']} --delete")


    utils.file_delete(os.path.join(get_env_var('TMPDIR_PATH'), 'provider'))
    utils.file_delete(os.path.join(get_env_var('TMPDIR_PATH'), 'random_tag'))
    utils.dir_delete(os.environ.get('VAGRANT_DOTFILE_PATH'))
    utils.echo('Temporary files removed')
    utils.echo('Destroy complete.')

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

def halt(ctx=None, *args, **params):
    if not ctx: # Using API. Else handled by cli.
        set_init_vars(params.get('cwd'), params.get('tmpdir_path'))
        set_vagrant_vars(params.get('vagrant_cwd'), params.get('vagrant_dotfile_path'))
    else:
        args = ctx.args + list(args)

    vagrant_general_command('{} {}'.format('halt', ' '.join(args)))

def install_auth(ctx=None, output_path=None, **params):
    '''Install auth directory.

    Agrs:
        ctx (object): Click Context object.
        output_path (path): Path to place auth dir.
    '''
    if not ctx: # Using API. Else handled by cli.
        set_init_vars(params.get('cwd'), params.get('tmpdir_path'))

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

def install_config(ctx=None, output_path=None, **params):
    '''Install config file.

    Agrs:
        ctx (object): Click Context object.
        output_path (path): Path to place conf file.
    '''
    if not ctx: # Using API. Else handled by cli.
        set_init_vars(params.get('cwd'), params.get('tmpdir_path'))

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

def install_plugins(force=None, plugins=('all',)):
    '''Install all of the vagrant plugins needed for all plugins

    Agrs:
        force (bool): Forces bypassing of reinstallation prompt.
        plugins (tuple): Names of vagrant plugins to install.
    '''
    host_system = platform.system()
    for plugin in plugins:
        if plugin == 'all':
            utils.echo('Installing all default plugins.')
            for plugin in SETTINGS['PLUGINS'][host_system]:
                _invoke_vagrant('plugin install %s' % plugin)
        elif plugin in SETTINGS['PLUGINS'][host_system]:
            _invoke_vagrant('plugin install %s' % plugin)
        else:
            if not force:
                click.confirm('The plugin "%s" is not in our list of plugins. Attempt '
                          'to install anyway?' % plugin, abort=True)
            vagrant_general_command('plugin install %s' % plugin)

def scp(ctx=None, locations=None, **params):
    '''Transfer file or dir with scp. This makes use of the vagrant-scp plugin,
    which allows for simplified args.
    '''
    if not ctx: # Using API. Else handled by cli.
        set_init_vars(params.get('cwd'), params.get('tmpdir_path'))
        set_vagrant_vars(params.get('vagrant_cwd'), params.get('vagrant_dotfile_path'))

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

def ssh(ctx=None, command=None, **params):
    '''Connect to an running VM / container over ssh.
    All str args can also be set as an environment variable; arg takes precedence.

    Agrs:
        ctx (object): Click Context object.
        command (str): Pass-through command to run with `vagrant ssh --command`.
        vagrant_cwd (path): Location of `Vagrantfile`. Used if invoked with API only.
        vagrant_dotfile_path (path): Location of `.vagrant` metadata directory. Used if invoked with API only.
    '''
    if not ctx: # Using API. Else handled by cli.
        set_init_vars(params.get('cwd'), params.get('tmpdir_path'))
        set_vagrant_vars(params.get('vagrant_cwd'), params.get('vagrant_dotfile_path'))

    ## Add pass-through 'command' option.
    cmd = 'vagrant ssh'
    if command:
        cmd = ' '.join([cmd, '--command', command])

    # do not use _invoke_vagrant, that will give a persistent ssh session regardless.
    os.system(cmd)

def up(ctx=None, **params):
    '''Start a VM / container with `vagrant up`.
    All str args can also be set as an environment variable; arg takes precedence.

    Agrs:
        ctx (object): Click Context object. Used to detect if CLI is used.
        params (dict): Dict of all args passed to `up`.

    In params, this looks for:
        provider (str): Provider to use.
        box (str): Vagrant box to use.
        cpus (int): Number of CPUs to give VirtualBox VM.
        guest_os (str): Guest OS to use.
        ram_size (int): RAM in MB to use.
        drive_size (int): Drive size in GB to use.
        machine_type (str): Machine type to use for cloud providers.
        sync_dirs (path): Paths to sync into VM.
        sync_type (str): Type of syncing to use.
        ports (str): Ports to forward.
        provision (bool): vagrant provisioning flag.
        provision_cmd (str): Command used at beginning of provisioning.
        provision_script (path): Path to script to use for provisioning.
        provision_with_salt (bool): Flag to indicate provisioning with salt.
        destroy_on_error (bool): vagrant destroy-on-error flag.
        vagrant_cwd (path): Location of `Vagrantfile`. Used if invoked with API only.
        vagrant_dotfile_path (path): Location of `.vagrant` metadata directory. Used if invoked with API only.
        vm_name (str): Name of the VM or container.
    '''
    # TODO: Add registering of VM for all of this installation to see

    if not ctx: # Using API. Else handled by cli.
        set_init_vars(params.get('cwd'), params.get('tmpdir_path'))
        set_vagrant_vars(params.get('vagrant_cwd'), params.get('vagrant_dotfile_path'))

    ## Option Handling - These might modify the params dict and/or set env vars.
    params['guest_os'] = options.guest_os_option(params.get('guest_os'))
    params['box'] = options.box_option(params.get('box'))
    params['cpus'] = options.cpus_option(params.get('cpus'))
    params['hostname'] = options.hostname_option(params.get('hostname'))
    params['machine_type'] = options.machine_type_option(params.get('machine_type'), params.get('provider'))
    params['project_dir'] = options.project_dir_option(params.get('project_dir'))
    params['provider'] = options.provider_option(params.get('provider'))
    params['provision_cmd'] = options.provision_cmd_option(params.get('provision_cmd'))
    params['provision_script'] = options.provision_script_option(params.get('provision_script'))
    params['provision_with_salt'] = options.provision_with_salt_option(params.get('provision_with_salt'))
    params['ram_size'], params['drive_size'] = options.size_option(
        params.get('ram_size'), params.get('drive_size')) # both ram and drive size
    params['salt_bootstrap_args'] = options.salt_bootstrap_args_option(params.get('salt_bootstrap_args'))
    params['sync_dirs'] = options.sync_dirs_option(params.get('sync_dirs'))
    params['sync_type'] = options.sync_type_option(params.get('sync_type'))
    params['ports'] = options.ports_option(params.get('ports'))
    params['vm_name'] = options.vm_name_option(params.get('vm_name'))

    cmd = 'up'

    ## Provider specific handling.
    ## Must come after all else, because logic may be done on params above.
    if params['provider'] == 'digitalocean':
        vagrant_providers.digitalocean()
    elif params['provider'] == 'docker':
        vagrant_providers.docker()
    elif params['provider'] == 'ec2':
        vagrant_providers.ec2()
    else:
        cmd += " --provider={}".format(params['provider'])

    ## Add straight pass-through flags. Keep test for True/False explicit as only those values should work
    if params.get('provision') is True:
        cmd = '{} {}'.format(cmd, '--provision')
    elif params.get('provision') is False:
        cmd = '{} {}'.format(cmd, '--no-provision')

    if params.get('destroy_on_error') is True:
        cmd = '{} {}'.format(cmd, '--destroy-on-error')
    elif params.get('destroy_on_error') is False:
        cmd = '{} {}'.format(cmd, '--no-destroy-on-error')

    vagrant_general_command(cmd)

def vagrant_general_command(cmd):
    '''Invoke vagrant with custom command.

    Args:
        cmd (str): String to append to command `vagrant ...`
    '''
    # Modify cmd in private function to keep enforcement of being a vagrant cmd there.
    _invoke_vagrant(cmd)


class Run_app():
    def __init__(self):
        print("in Run_app __init__")
