import digitalocean

def up(params, ctx):
    token="#####"
    manager = digitalocean.Manager(token=token)
    my_droplets = manager.get_all_droplets()
    print(my_droplets)

    manager = digitalocean.Manager(token=token)
    keys = manager.get_all_sshkeys()
    droplet = digitalocean.Droplet(token=token,
                                   name='Example',
                                   region='nyc1',
                                   image='ubuntu-20-04-x64',
                                   size_slug='s-1vcpu-1gb',
                                   ssh_keys=keys,
                                   backups=True)
    droplet.create()

def halt(ctx, args, params):
    print("stub")
