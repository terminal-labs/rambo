import rambo.utils as utils
from rambo.settings import SETTINGS, PROJECT_LOCATION, PROJECT_NAME
from rambo.utils import get_env_var, set_env_var

def provider_option(params):
    '''Validate provider. If not supplied, set to default. Set as env var.

    Args:
        params (dict): Dict of all args passed to `up`.

    In params, this takes:
        provider (str): Provider to use.

    Return params (dict)
    '''
    if not params['provider']:
        params['provider'] = SETTINGS['PROVIDERS_DEFAULT']
    set_env_var('provider', params['provider'])

    if params['provider'] not in SETTINGS['PROVIDERS']:
        msg = ('Provider "%s" is not in the provider list.\n'
           'Did you have a typo? Here is as list of avalible providers:\n\n'
           % params['provider'])
        for supported_provider in SETTINGS['PROVIDERS']:
            msg = msg + '%s\n' % supported_provider
        utils.abort(msg)
    return params

def guest_os_option(params):
    '''Validate guest_os. If not supplied, set to default. Set as env var.

    Args:
        params (dict): Dict of all args passed to `up`.

    In params, this takes:
        guest_os (str): Guest OS to use.

    Return params (dict)
    '''
    if not params['guest_os']:
        params['guest_os'] = SETTINGS['GUEST_OSES_DEFAULT']
    set_env_var('guest_os', params['guest_os'])

    if params['guest_os'] not in SETTINGS['GUEST_OSES']:
        msg = ('Guest OS "%s" is not in the guest OSes whitelist.\n'
               'Did you have a typo? We\'ll try anyway.\n'
               'Here is as list of avalible guest OSes:\n\n'
               % params['guest_os'])
        for supported_os in SETTINGS['GUEST_OSES']:
            msg = msg + '%s\n' % supported_os
        utils.warn(msg)
    return params

def size_option(params):
    '''Validate ram and drive sizes. Pair them if possible. If not
    supplied, set to default. Set as env var. Reset in params as strings.

    Args:
        params (dict): Dict of all args passed to `up`.

    In params, this takes:
        ram_size (int): RAM in MB to use.
        drive_size (int): Drive size in GB to use.

    Return params (dict)
    '''
    # Cast to strings if they exist so they can stored as env vars.
    if params['ram_size']:
        params['ram_size'] = str(params['ram_size'])
    if params['drive_size']:
        params['drive_size'] = str(params['drive_size'])

    if params['ram_size'] and not params['drive_size']:
        try:
            params['drive_size'] = SETTINGS['SIZES'][params['ram_size']]
        except KeyError: # Doesn't match, but we'll let them try it.
            params['drive_size'] = SETTINGS['DRIVESIZE_DEFAULT']
    elif params['drive_size'] and not params['ram_size']:
        try:
            params['ram_size'] = list(SETTINGS['SIZES'].keys())[
                list(SETTINGS['SIZES'].values()).index(params['drive_size'])]
        except ValueError: # Doesn't match, but we'll let them try it.
            params['ram_size'] = SETTINGS['RAMSIZE_DEFAULT']
    elif not params['ram_size'] and not params['drive_size']:
        params['ram_size'] = SETTINGS['RAMSIZE_DEFAULT']
        params['drive_size'] = SETTINGS['DRIVESIZE_DEFAULT']
    # else both exist, just try using them

    set_env_var('ramsize', params['ram_size'])
    set_env_var('drivesize', params['drive_size'])

    ## ram_size
    if params['ram_size'] not in iter(SETTINGS['SIZES']):
        msg = ('RAM Size "%s" is not in the RAM sizes list.\n'
               'Did you have a typo? We\'ll try anyway.\n'
               'Here is as list of avalible RAM sizes:\n\n'
               % params['ram_size'])
        for supported_ram_size in iter(SETTINGS['SIZES']):
            msg = msg + '%s\n' % supported_ram_size
        utils.warn(msg)

    ## drive_size
    if params['drive_size'] not in iter(SETTINGS['SIZES'].values()):
        msg = ('DRIVE Size "%s" is not in the DRIVE sizes list.\n'
               'Did you have a typo? We\'ll try anyway.\n'
               'Here is as list of avalible DRIVE sizes:\n\n'
               % params['drive_size'])
        for supported_drive_size in iter(SETTINGS['SIZES'].values()):
            msg = msg + '%s\n' % supported_drive_size
        utils.warn(msg)
    return params

def machine_type_option(params):
    '''Validate machine_type. If not supplied, set to default. Set as env var.

    Args:
        params (dict): Dict of all args passed to `up`.

    In params, this takes:
        machine_type (str): Machine type to use for cloud providers.

    Return params (dict)
    '''
    if params['machine_type']:
        if params['provider'] in ('docker', 'lxc', 'virtualbox'):
            msg = ('You have selected a machine-type, but are not using\n'
                   'a cloud provider. You selected %s with %s.\n'
                   % (params['machine_type'], params['provider']))
            utils.abort(msg)
        set_env_var('machinetype', params['machine_type'])
    return params
