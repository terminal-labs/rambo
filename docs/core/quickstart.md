# Quickstart

## Hardware Recommendations
For running VMs locally in VirtualBox (default), we suggest a minimum of:

* Reasonably fast cpu with 2 cores and virtualization hardware support (e.g. an Intel i7-3612QM 2.1GHz, 4 core chip with VT-x)
* 8GB RAM
* 16GB free drive space

For running containers locally (e.g. LXC) or spawning cloud based VMs (e.g. AWS EC2) you can get away with comparatively slow computer and you don't need VT-x, you don't even need VirtualBox. In fact, these providers can be managed from just a [Raspberry Pi](https://www.raspberrypi.org/).

## Supported Host Operating Systems

- [Ubuntu 16.04 or newer](https://www.ubuntu.com/download/desktop)

- [OSX](https://www.apple.com/mac-mini/)

We expect it's likely you can get Rambo to work on any Unix-like system, but your milleage may vary. So far we have made no effort to get this working with Windows. Contributions are very welcome.

## Installation

1. Install / Use Python 3.2+ and pip (for example with a Virtual Environment).

1. Download and install [VirtualBox](https://www.virtualbox.org/) 5.1 or newer.

1. Download and install [Vagrant](https://www.vagrantup.com/).

1. Install Rambo with pip,

    - [latest release](https://github.com/terminal-labs/rambo/releases) with pypi: `pip install rambo-vagrant`, or
    - [from source](https://github.com/terminal-labs/rambo): `git clone git@github.com:terminal-labs/rambo.git --recursive; cd rambo; pip install -e .`

1. Install plugins with `rambo install-plugins`


Note: Vagrant and VirtualBox update frequently, and sometimes with breaking changes. Additionally there are may be provider specific dependencies.

## Create Project

Now that Rambo is installed, you must initialize a project. This will create a directory that will be tied to your VM. Outside of this directory, Rambo won't be able to find the VM to control it. This also means that if you want to create or control multiple VMs with Rambo, you can, by simply creating more projects and running Rambo commands from the directories where they reside. Create and go to your project:

```
rambo createproject yourprojectname
cd yourprojectname
```

In this project directory Rambo gave you a few things to help you get started, a `rambo.conf`, `auth` dir, and `saltstack` dir. These are basic configs to start you out. You don't need to modify them for basic use.

## Providers

Rambo supports various providers, and aims to let you switch between them as easily as possible. Nevertheless, some providers do have particular considerations, such as setting up keys and payment for cloud services, or specific dependencies for the host OS. This is a list of Rambo's supported providers, with links to specific documentation pages for each.

- [AWS EC2](../../providers/aws-ec2)
- [DigitalOcean](../../providers/digitalocean)
- [Docker](../../providers/docker)
- [LXC](../../providers/lxc)
- VirtualBox (see below)

### Default Provider - VirtualBox:

If you never specify any provider, Rambo will use the VirtualBox as its default choice, and is simply

`rambo up`

or the identical, more verbose command

`rambo up -p virtualbox`
