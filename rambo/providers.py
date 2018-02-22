import json
import os

from rambo.settings import SETTINGS
from rambo.utils import get_env_var, set_env_var

def aws_ec2():
    if get_env_var('guest_os'): # only set during `up`
        set_env_var('ami', SETTINGS['GUEST_OSES'][get_env_var('guest_os')]['ec2'])

def digital_ocean():
    pass

def load_provider_keys():
    aws_ec2()
    digital_ocean()
