import json
import os

from rambo.settings import SETTINGS
from rambo.utils import abort, get_env_var, set_env_var

def digitalocean():
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
    if get_env_var('guest_os'): # only set during `up`
        set_env_var('docker_box', SETTINGS['GUEST_OSES'][get_env_var('guest_os')]['docker'])

def ec2():
    if get_env_var('guest_os'): # only set during `up`
        set_env_var('ami', SETTINGS['GUEST_OSES'][get_env_var('guest_os')]['ec2'])
    if get_env_var('ramsize') not in SETTINGS['SIZES']:
        abort('Sorry, we really need a RAM size from our whitelist for '
              'digitalocean. \nThe only way around that is if you specify '
              'a machine-type like m3.medium.')

def load_provider_keys():
    ec2()
    digital_ocean()
