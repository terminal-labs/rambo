# CLI

Rambo's CLI is the expected normal way people interact with Rambo. At it's core, Rambo is an interface to Vagrant. Rambo duplicates several commands from Vagrant, that are either commonly used, or Rambo needs to do some preemptive work for before passing the reigns to Vagrant. For most other Vagrant commands, you can call Vagrant through Rambo. Many commands have various options that have defaults that are used when the option is not specified, e.g. `rambo up` defaults using VirtualBox as the `provider`.

This is a short list of Rambo's commands, followed by a more detailed explanation of each:

## Commands

- [createproject](#createproject): Create a Rambo project dir with basic setup.
- [destroy](#destroy): Destroy a VM / container and all its metadata. Default leaves logs.
- [export-vagrant-conf](#export-vagrant-conf): Get Vagrant configuration.
- [halt](#halt): Halt VM.
- [install-plugins](#install-plugins): Install Vagrant plugins.
- [scp](#scp): Transfer files with scp.
- [ssh](#ssh): Connect with `vagrant ssh`
- [up](#up): Start a VM / container with `vagrant up`.
- [vagrant](#vagrant): Run a Vagrant command through Rambo.

### createproject

Create project takes an arguement for the name to give to the project it creates. It will create a directory in the CWD for this project. Upon creation, this project directory will contain a `rambo.conf` file, an `auth` directory, and a `saltstack` directory.

- `rambo.conf` is the config file that is required to be present in your project to run `rambo up`, and is described [later in conf.md](../conf).
- `auth` contains some sample scripts that will aid in setting up keys / tokens for the cloud providers. It is not required. How to use that is described in the cloud provider specific documentation.
- `saltstack` is a basic set of SaltStack configuration code that Rambo offers. [It can be modified for custom configuration.](../customizing)

### destroy

Destroy a VM / container. This will tell vagrant to forcibly destroy a VM, and to also destroy its Rambo metadata (provider and random_tag), and Vagrant metadata (`.vagrant` dir).

### export-vagrant-conf

Places the default `Vagrantfile` and its resources (`vagrant` dir, `settings.json`) in the CWD for [customizing](../customizing).

### halt

Tells Vagrant to 'halt' the VM. Useful to free the Host's resources without destroying the VM.

### install-plugins

 Install passed args as Vagrant plugins. `all` or no args installs all default Vagrant plugins from host platform specific list.

### scp

Transfer files or directories with scp. Accepts two args in one of the
following forms:

    <local_path> <remote_path>

    <local_path> :<remote_path>

    :<remote_path> <local_path>

    <local_path> [vm_name]:<remote_path>

    [vm_name]:<remote_path> <local_path>

For example: `rambo scp localfile.txt remotefile.txt`

### ssh

Connect to the VM / container over SSH. With `-c` / `--command`, will executed an SSH command directly.

### up

Start a VM or container. Will create one and begin provisioning it if it did not already exist. Accepts many options to set aspects of your VM. Precedence is CLI > Config > Env Var > defaults.

### vagrant

Accepts any args and forwards them to Vagrant directly, allowing you to run any Vagrant command. Rambo has first-class duplicates or wrappers for the most common Vagrant commands, but for less common commands or commands that are not customized, they don't need to be duplicated, so we call them directly.

## rambo.conf

The `rambo.conf` file is used to add options to various Rambo commands without having to pass them to the CLI. This is encouraged and has a few benefits. See the following quick example:

```ini
[up]
provider = digitalocean
guest_os = centos-7
```

is equivalent to:

```bash
rambo up --provider digitalocean --guest-os centos-7
```

For a more detailed description, see the separate [rambo.conf docs](../conf).

## Environment Variables

**This is advanced and shouldn't be used without good reason.**

Like the config file, options can also be specified as environment variables. However, this is much more complex, and we strongly recommend not using these manually, as we think it's much easier to lose track of what's going on and cause undue headache. If you really need to know, look at this specific page for [Environment Variables](../env_vars).
