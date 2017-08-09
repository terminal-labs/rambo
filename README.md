# README

## Installation
To get up and running fast, see: [INSTALL.md](https://github.com/terminal-labs/rambo/blob/master/docs/INSTALL.md)

## What Is This Repository For?
This repo is for provisioning and configuration of virtual machines (and containers) in a simple and predictable way. Just run one command and your vms is up, code is deployed and your app is running, on any supported platform.

At this time the repo allows you to create a debian 8 Jessie VM on multiple providers (AWS EC2, Digitalocean, Virtualbox, lxc) The base machine configuration is a debian 8 Jessie 64bit os with 1024mb ram, and 30GB drive.

One of the goals of this project is be able to run a simple command (`vagrant up` with some extra custom commands) and have a new vm be created on your provider of choice. Once the vms is initialized saltstack is used to deploy code to your machine and saltstack is also used to otherwize configure the machine. The saltstack machine configuration code (states) will run the same regardless of which provider is actually running the machine.

Another goal of this repo is to have the spawned vms be maximally similar across providers. Usually, your application will not need to change at all and will simply run on all providers.

Since this project uses vagrant and vagrant plugins for the heavy lifting many core vagrant functions still work here on all providers, such as `up`, `ssh`, `destroy`, and `rsync`. All machines, regardless of provider, will also copy the entire cwd (this repo and it's, hidden subdirs, and included sensitive files) into the guest machine. From inside the guest the dir is located at `/vagrant/salt_resources`. Note: this dir copy process is done once on `vagrant up` via rsync, after that no automatic syncing will occur. `vagrant rsync` and `vagrant rsync-auto` can be used to rsync a running vm.

By default Rambo offers a basic provisioning, but you can customize this. See **Advanced Usage** for that.

## Basic Usage
Once some simple installation and configuration steps are complete you can run one of these commands to get your vm:

for VirtualBox run
```
#!bash
$ vagrant --target=virtualbox up
$ vagrant ssh
```

for LXC run
```
#!bash
$ vagrant --target=lxc up
$ vagrant ssh
```

for DigitalOcean run
```
#!bash
$ vagrant --target=digitalocean up
$ vagrant ssh
```

for AWS EC2 run
```
#!bash
$ vagrant --target=ec2 up
$ vagrant ssh
```

Note on Host Platform Support: LXC is only supported on Ubuntu 16. The other 3 providers also work on Mac. No testing has been done on Windows.

## Advanced Usage

### SSH Alias: Key Sharing and Emacs

Rambo defaults to using a priveleged user (e.g. `vagrant`, `root`) to provision the machine when it's spawned, but also to create a non-priveleged or deescalated user. This user is for development and for specific production server tasks that do not require root priviliges. Vagrant defaults to only sharing keys with the rooted user, so, you may need to share your keys deliberately with the deescalated user if your working there manually (such as during development.) Assuming Rambo is configuring a deescalated user called `webserver`, here's how.

After logging in with `vagrant ssh`,

```
#!bash

cd /home/webserver
sudo setfacl -m webserver:x $(dirname "$SSH_AUTH_SOCK")
sudo setfacl -m webserver:rwx "$SSH_AUTH_SOCK"
sudo su webserver
```

Alternatively, you may want to make this into a handy alias to ssh into the virtual machine.
Using the above commands instead is tedious, and will have to be repeated every time you want to ssh in and use this deescalated user.
Using an alias is much more convenient.

Emacs users will like to add a last line for `script /dev/null` to allow emacsclient to work correctly as the development user.
**`script /dev/null` is unsafe and should not be used in production.**

To create this alias, append this to your .bashrc file:

```
#!bash

alias vssh="vagrant ssh -- -t 'cd /home/webserver;\
    sudo setfacl -m webserver:x \$(dirname \"\$SSH_AUTH_SOCK\");\
    sudo setfacl -m webserver:rwx \"\$SSH_AUTH_SOCK\";\
    sudo su webserver'\
    -c 'script /dev/null'"
```

Just swap out `webserver` for another user if you changed this user name in your Rambo configuration.

### Custom Provisioning
Rambo provides a basic default provisioning with Vagrant and Salt Stack. To build out what you need for your project you will need your own customized provisioning. You can do this provisioning with any tool you like through Vagrant, such as with shell scripts, Salt Stack, or any other provisioning tool.

Rambo has a few Salt States available that are commented out that you can 'turn on' and use. You will need to uncomment any states you want in the `salt_resources/states/top.sls` file. Then you will need to uncomment and supply your relevant data in the `salt_resources/grains/grains` file. Of course you can add your own as well.

You can add your custom Salt States right into the Salt code and they should be automatically picked up and used. If you want to add provisioning with any other tool, you will need to modify the Vagrantfiles found in `vagrant_resources/vagrant/` to add that provisioning.

## Contributing
We heartily welcome any contirubtions to this project, whether in the form of commenting on or posting an issue, or development. If you would like to submit a pull request, you might first want to look at our development guidlines for this project in [RULES.md](https://github.com/terminal-labs/rambo/blob/master/RULES.md)

## Special Thanks
Thanks go out to the Vagrant community and HashiCorp. Vagrant is a great tool it has helped us a lot over the years.
