# CLI

**Caution: The CLI is young and subject to breaking changes without notice.**

Rambo's CLI is the expected normal way people interact with Rambo. At it's core, Rambo is an interface to Vagrant. Rambo duplicates several commands from Vagrant, that are either commonly used, or Rambo needs to do some preemptive work for before passing the reigns to Vagrant. For most other Vagrant commands, you can call Vagrant through Rambo. Many commands have various options that have defaults that are used when the option is not specified, e.g. `rambo up` defaults using VirtualBox as the `provider`.

This is a list of Rambo's commands:

## Commands

- `createproject`: Create a Rambo project dir with basic setup.
- `destroy`: Destroy a VM / container and all its metadata. Default leaves logs.
- `export-vagrant-conf`: Get Vagrant configuration.
- `install-plugins`: Install Vagrant plugins.
- `ssh`: Connect with `vagrant ssh`
- `up`: Start a VM / container with `vagrant up`.
- `vagrant`: Run a vagrant command through rambo.

## rambo.conf

The `rambo.conf` file is required at the top level in your project directory. It is an INI config file that can specify options on various commands. Options passed to the CLI will take precedence over options set via this config file. If you're repeating the same CLI options, setting those options in this config might make your life a little easier. Further, if you intend on tracking your Rambo project in version control, it can be very handy to set some options in this config that match the purpose of your project.

Options on the base `rambo` command and the subcommand `up` can be set in `rambo.conf`. The INI section refers to the command used in the CLI, and the keys/values within that section refers to the options being set on that command. For example, a useful `rambo.conf` could look like this:

```ini
[up]
provider = digitalocean
guest_os = centos-7
```

which is equivalent to:

```bash
rambo up -p digitalocean -o centos-7
```

Setting the config file to this allows you to type simply `rambo up` to run `up` with the `provider` and `guest-os` options set. Note that dashes in CLI options need to be underscores in the config file. If these options are set, to switch providers, but keep the same guest-os, you would only need to set the provider option in the CLI. For example, `rambo up -p ec2` would set the provider to be `ec2`, taking precedence over the `digitalocean` set in the config, but still use the guest-os `centos-7` set in the config.

## Environment Variables

**This is advanced and shouldn't be used without good reason.**

Like the config file, options can also be specified as environment variables. However, this is much more complex, and we strongly recommend not using these manually, as we think it's much easier to lose track of what's going on and cause undue headache. If you really need to know, look at this specific page for [Environment Variables](env_vars.md).
