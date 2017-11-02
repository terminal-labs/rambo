# README

## Installation
To get up and running fast, see: [INSTALL.md](https://github.com/terminal-labs/rambo/blob/master/docs/INSTALL.md)

## What Is This Repository For?
This project is for provisioning and configuration of virtual machines (and containers) in a simple, predictable, and highly reproducible way. Just run one command and your VM is up, code is deployed, and your app is running, on any supported platform.

At this time this repo allows you to create a Debian 8 Jessie VM on multiple providers (AWS EC2, DigitalOcean, VirtualBox, LXC). Several more Operating Systems are available on select providers. The base machine configuration is a Debian 8 Jessie 64bit OS with 1024MB RAM, and 30GB drive.

One of the goals of this project is be able to run a simple command and have a new VM be created on your provider of choice. Once the VM is initialized SaltStack is used to deploy code to and provision your machine. The SaltStack machine configuration code (states) will run the same regardless of which provider is actually running the machine.

Another goal of this repo is to have the spawned VMs be maximally similar across providers. Usually, your application will not need to change at all and will simply run on all providers.

This project uses Vagrant and Vagrant plugins for some of the heavy lifting, and many core Vagrant functions still work here on all providers, such as `up`, `ssh`, `destroy`, and `rsync`. Any command that Rambo doesn't use is simply passed to Vagrant.

By default Rambo offers a basic provisioning, but you can customize this. See [**Advanced Usage**](#advanced-usage) for that.

## Basic Usage
Rambo needs to be installed first. It is a Python package, and can be installed in an Conda or Virtualenv environment with `pip install rambo-vagrant`, or the development version (this repo) can be installed with `pip install -e .`. Some providers will need a more configuration for things like key managment (see: [INSTALL.md](https://github.com/terminal-labs/rambo/blob/master/docs/INSTALL.md)). Once installed, you can run one of these commands to get your VM:

for VirtualBox run
```
$ rambo up
$ rambo ssh
```

for AWS EC2 run
```
$ rambo up -p ec2
$ rambo ssh
```

for DigitalOcean run
```
$ rambo up -p digitalocean
$ rambo ssh
```

for Docker run
```
$ rambo up -p docker
$ rambo ssh
```

for LXC run
```
$ rambo up -p lxc
$ rambo ssh
```

Note on host platform support: LXC is only supported on Ubuntu 16. The other providers also work on Mac and should work on any Unix-like system. No testing has been done on Windows.

## Advanced Usage

### Custom Provisioning
Rambo provides a basic default provisioning with Vagrant and SaltStack. To build out what you need for your project you will need your own customized provisioning. You can do this provisioning with any tool you like through Vagrant, such as with shell scripts, SaltStack, or any other provisioning tool.

All Rambo code that is used to provision the VM is kept where Rambo is installed. This directory is copied into the VM at an early stage in the spawn process so that it can be invoked to provision the VM.

Rambo has a few Salt States available that are commented out that you can 'turn on' and use. You will need to uncomment any states you want in the `salt_resources/states/top.sls` file. Then you will need to uncomment and supply your relevant data in the `salt_resources/grains/grains` file. Of course you can add your own as well.

You can add your custom Salt States right into the Salt code and they should be automatically picked up and used. If you want to add provisioning with any other tool, you will need to modify the Vagrantfiles found in `vagrant_resources/vagrant/` to add that provisioning.

### CLI and Python API

**Both the CLI and Python API are young and subject to breaking changes without notice.**


Rambo has a CLI and Python API that are compatible. In other words, what you can do in the CLI, you can do in the Python API. To accomplish this the CLI is largely dependant on the Python API. You can access the Python API by importing the various functions in app.py, such as with `from rambo.app import vagrant_up`

Through the Python API you can call `vagrant_up` and `vagrant_destroy` to create and destroy VMs. `vagrant_ssh` is also available and presents an interactive shell to the VM, as if you ran `rambo ssh` with the CLI.

CLI options are available to be set as either functions in app.py, or as parameters to those functions, depending on whether the CLI option was on `rambo` command itself or a subcommand (e.g. `up`). For instance, the following are equivalent:

```
$ rambo --vagrant-cwd /path up -p virtualbox
```
```
from rambo.app import set_vagrant_vars, vagrant_up
set_vagrant_vars(vagrant-cwd,"/path")
vagrant_up(provider="virtualbox")
```

Currently, all of the CLI options can also be set as environment variables. Environment variables are respected by both the CLI and Python API, but are overridden when set with a CLI option / Python API param.

### Environment Variables

The following environment variables are used by Rambo:

- `VAGRANT_DOTFILE_PATH` - [This is used by Vagrant directly](https://www.vagrantup.com/docs/other/environmental-variables.html#vagrant_dotfile_path), and is able to be set via the CLI / API.
- `VAGRANT_CWD` - [This is used by Vagrant directly](https://www.vagrantup.com/docs/other/environmental-variables.html#vagrant_cwd), and is able to be set via the CLI / API.
- `RAMBO_ENV` - This is the location of the project environment Rambo's code lives in. It is generated internally and not able to be set with the CLI / API.
- `RAMBO_TMP` - This is the location of Rambo's metadata folder specific to each VM. It is automatically placed in the CWD when the CLI / API is used.
- `RAMBO_PROVIDER` - This is the provider that is being used. It is able to be set via the CLI / API.

### SSH Alias: Key Sharing and Emacs

**The following is deprecated with Rambo's new CLI / API**

Rambo defaults to using a priveleged user (e.g. `vagrant`, `root`) to provision the machine when it's spawned, but also to create a non-priveleged or deescalated user. This user is for development and for specific production server tasks that do not require root priviliges. Rambo defaults to only sharing keys with the rooted user, so you may need to share your keys deliberately with the deescalated user if you're working there manually (such as during development.) Assuming Rambo is configuring a deescalated user called `webserver`, here's how.

After logging in with `rambo ssh`,

```
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
alias vssh="vagrant ssh -- -t 'cd /home/webserver;\
    sudo setfacl -m webserver:x \$(dirname \"\$SSH_AUTH_SOCK\");\
    sudo setfacl -m webserver:rwx \"\$SSH_AUTH_SOCK\";\
    sudo su webserver'\
    -c 'script /dev/null'"
```

Just swap out `webserver` for another user if you changed this user name in your Rambo configuration.

## Contributing
We heartily welcome any contirubtions to this project, whether in the form of commenting on or posting an issue, or development. If you would like to submit a pull request, you might first want to look at our development guidlines for this project in [RULES.md](https://github.com/terminal-labs/rambo/blob/master/RULES.md)

## Special Thanks
Thanks go out to the Vagrant community and HashiCorp. Vagrant is a great tool it has helped us a lot over the years.
