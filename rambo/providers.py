import json
import os

from rambo.settings import SETTINGS
from rambo.utils import abort, get_env_var, set_env_var

def aws_ec2():
    if get_env_var('guest_os'): # only set during `up`
        set_env_var('ami', SETTINGS['GUEST_OSES'][get_env_var('guest_os')]['ec2'])
    if get_env_var('ramsize') not in SETTINGS['SIZES']:
        abort('Sorry, we really need a RAM size from our whitelist for ec2.\n'
              'The only way around that is if you specify a machine-type like m3.medium.')

def digital_ocean():
    pass

def load_provider_keys():
    aws_ec2()
    digital_ocean()
