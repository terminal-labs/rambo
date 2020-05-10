from rambo.ops.synthetic import up as synthetic_up, halt as synthetic_halt, destroy as synthetic_destroy, ssh as synthetic_ssh, scp as synthetic_scp
from rambo.ops.virtualbox import up as virtualbox_up, halt as virtualbox_halt,  destroy as virtualbox_destroy, ssh as virtualbox_ssh, scp as virtualbox_scp

def ops_up(cmd, params):
    if params['provider'] == "synthetic":
        synthetic_up(cmd, params)
    if params['provider'] == "virtualbox":
        virtualbox_up(cmd, params)

def ops_destroy(cmd, params):
    print(params['provider'])
    if params['provider'] == "synthetic":
        synthetic_destroy(cmd, params)
    if params['provider'] == "virtualbox":
        virtualbox_destroy(cmd, params)

def ops_halt(cmd, params):
    if params['provider'] == "synthetic":
        synthetic_halt(cmd, params)
    if params['provider'] == "virtualbox":
        virtualbox_halt(cmd, params)

def ops_ssh(cmd, params):
    if params['provider'] == "synthetic":
        synthetic_ssh(cmd, params)
    if params['provider'] == "virtualbox":
        virtualbox_ssh(cmd, params)

def ops_scp(cmd, params):
    if params['provider'] == "synthetic":
        synthetic_scp(cmd, params)
    if params['provider'] == "virtualbox":
        virtualbox_scp(cmd, params)
