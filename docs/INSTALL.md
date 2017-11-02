# Setup and Installation

## Hardware Recommendations
For running VMs locally in VirtualBox, we suggest a minimum of:

* Reasonably fast cpu with 2 cores and VT-x (e.g. an Intel i7-3612QM 2.1GHz, 4 core chip)
* 8GB ram
* 16GB free drive space

For running containers in LXC locally or spawning machine in AWS EC2/DigitalOcean you can get away with comparatively slow computer and you don't need VT-x. In fact, the LXC/EC2/DigitalOcean providers can be managed from a Raspberry Pi. See: https://www.raspberrypi.org/

## Summary of Setup:
You need to install some programs into your host for certain providers, then you will need to install some Vagrant plugins. You also need to setup full accounts (or login into existing accounts) at any cloud provider you want to use.

## Supported Host OS:
[Ubuntu 16.04 or newer](https://www.ubuntu.com/download/desktop)

[OSX](http://www.apple.com/mac-mini/)

We expect it's likely you can get Rambo to work on any Unix-like system, but your milleage may vary. We have made no effort to get this working with Windows. Contributions are welcome.

## Dependencies:

Download and install VirtualBox and Vagrant.

- [VirtualBox 5.1 or newer](https://www.virtualbox.org/)

- [Vagrant](http://www.vagrantup.com/)

- [Vagrant Plugins](https://github.com/terminal-labs/rambo/blob/master/docs/INSTALL.md#install-vagrant-plugins)

Note: Vagrant and VirtualBox update frequently, and sometimes with breaking changes. Additionally there are host OS specific dependencies below.

### Dependencies (Ubuntu):
You first need to install some dependencies for your host OS. For Ubuntu based systems, run:

```
sudo apt install -y build-essential linux-headers-$(uname -r) lxc lxc-templates cgroup-lite redir xclip
```

### Dependencies (Mac):

There are no additional dependencies for Mac, however, LXC cannot be used as a provider at this time.

### Install Vagrant Plugins:
cd into the `rambo` repo and run:

```
./rambo/setup.sh
```

# Providers

Rambo supports various providers, and aims to let you switch between them as easily as possible. Nevertheless, some providers do have particular considerations, such as setting up keys and payment for cloud services, or specific dependencies for the host OS. This is a list of Rambo's supported providers, with links to specific documentation pages for each.

- [AWS EC2](https://github.com/terminal-labs/rambo/blob/master/docs/providers/aws-ec2.md)
- [DigitalOcean](https://github.com/terminal-labs/rambo/blob/master/docs/providers/digitalocean.md)
- [Docker](https://github.com/terminal-labs/rambo/blob/master/docs/providers/docker.md)
- [LXC](https://github.com/terminal-labs/rambo/blob/master/docs/providers/lxc.md)
- [VirtualBox](https://github.com/terminal-labs/rambo/blob/master/docs/INSTALL.md#virtualbox-provider)

## VirtualBox Provider:

Assuming that you installed the dependencies you should be able to run 

`rambo up`

or the more verbose command 

`rambo up -p virtualbox`
