

from rambo.utils import abort

def destroy():
    # return for local cleanup, don't abort
    print('gce destroy')

def halt():
    abort('gce halt')

def scp(locations):
    abort('gce scp')

def ssh():
    abort('gce ssh')

def up(**params):
    print('gce up')
    print(params)
    abort('got google?')
