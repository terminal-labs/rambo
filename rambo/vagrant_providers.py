import json
import os

from rambo.settings import SETTINGS
from rambo.utils import abort, get_env_var, set_env_var

def digitalocean():
    '''DigitalOcean specific preparation for Vagrant. Setting and validating env vars.

    Set env vars: do_image

    Sanitize against non-whitelist ramsize and drivesize.
    '''
    if get_env_var('guest_os'): # only set during `up`
        set_env_var('do_image', SETTINGS['GUEST_OSES'][get_env_var('guest_os')]['do'])
    if get_env_var('ramsize') not in SETTINGS['SIZES']:
        abort('Sorry, we really need a RAM size from our whitelist for '
              'digitalocean. \nThe only way around that is if you specify '
              'a machine-type like s-8vcpu-32gb.')
    if get_env_var('drivesize') not in SETTINGS['SIZES'].values():
        abort('Sorry, we really need a drive size from our whitelist for '
              'digitalocean. \nThe only way around that is if you specify '
              'a machine-type like s-8vcpu-32gb.')
def docker():
    '''Docker specific preparation for Vagrant. Setting and validating env vars.

    Set env vars: docker_box
    '''
    if get_env_var('guest_os'): # only set during `up`
        set_env_var('docker_box', SETTINGS['GUEST_OSES'][get_env_var('guest_os')]['docker'])

def ec2():
    '''EC2 specific preparation for Vagrant. Setting and validating env vars.

    Set env vars: ami

    Sanitize against non-whitelist ramsize.
    '''
    if get_env_var('guest_os'): # only set during `up`
        set_env_var('ami', SETTINGS['GUEST_OSES'][get_env_var('guest_os')]['ec2'])
    if get_env_var('ramsize') not in SETTINGS['SIZES']:
        abort('Sorry, we really need a RAM size from our whitelist for '
              'digitalocean. \nThe only way around that is if you specify '
              'a machine-type like m3.medium.')
