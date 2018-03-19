import salt.cloud

## This will requer rambo to be run from exactly one level deep into a project dir. Will need to be generalized alter.
client = salt.cloud.CloudClient(path='saltstack/cloud.profiles')

from rambo.utils import abort

def destroy():
    client.destroy(names=['instance-2'])
    # return for local cleanup, don't abort
    print('gce destroy')

def halt():
    abort('gce halt')

def scp(locations):
    abort('gce scp')

def ssh():
    abort('gce ssh')

def up(**params):
    ## We might consider reading params here and updating the 'profile' as the profile is what salt actualy looks to for direction.
    ## If we can dig enough into the salt code, we might be able to evoid that and push configuration directly, but they might not have
    ## made that very easy.
    print('gce up')
    print(params)
    client.profile('my-gce-profile',names=['instance-2']) 
    abort('got google?')
