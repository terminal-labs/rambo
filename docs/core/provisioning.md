# Basic Provisioning

By default Rambo will do a small amount of basic provisioning. It will:

- Set the hostname
- Sync your project directory
- Sync custom directories
- Run a custom command

## Hostname

The hostname can be set by specifying the `--hostname` option.

## Syncing

### Sync Types

The default syncing method is whatever Vagrant uses as its default ([link](https://www.vagrantup.com/docs/synced-folders/basic_usage.html#type)).

> Vagrant will automatically choose the best synced folder option for your environment.

For basic usage, that means the default for Rambo, using the VirtualBox provider, is shared folders.

This can be changed to any of the syncing methods that Vagrant supports; see [their docs](https://www.vagrantup.com/docs/synced-folders/) for details. Syncing can also be entirely disabled. Common options are:

- `disabled`
- `rsync`
- `shared`

These can be specified with `--sync-type`.

`--sync-type disabled` turns off syncing entirely.

### Synced directories

Rambo will sync your project directory and any custom directories. The following mappings are synced in the order listed.

| Host (source)                   | VM (target)           |
|---------------------------------|-----------------------|
| [ project dir]                  | /vagrant              |
| custom dirs on host             | custom dirs on VM     |


Custom dirs can be passed to `--sync-dirs` as a list of lists of the form

```
--sync-dirs "[['path on host', 'absolute path on VM'], ['second path on host', 'second absolute path on VM']]"
```

This list of lists must

- be able to be evaluated by Python and Ruby as a list of lists of strings,
- specify target paths with absolute paths

Since this is rather cumbersome to pass in the CLI, remember that it can also be set in the [configuration file](../core/conf), like

```
[up]
sync_dirs = [['path on host', 'absolute path on VM'], ['second path on host', 'second absolute path on VM']]
```

## Command Provisioning

Rambo is able to provision with a command. This command can be passed to `rambo up` in the cli, or set in the `rambo.conf`. For example:

```shell
rambo up -c "hostname"
```

will provision and run the command `hostname`, displaying the hostname of the instance as part of the provisioning process.

This command is intended to be the entry point to any user-controlled way of provisioning, and easily used with other synced code. For instance, this command could run a script, or invoke configuration management tools like Salt or Puppet.

For example, this setup will run a command, that calls a custom script that installs Salt and runs a highstate. This example works as-is with the basic Salt setup that Rambo provides in a new project.

```ini
# rambo.conf

[up]
provider = virtualbox
box = ubuntu/bionic64
sync_dirs = [["saltstack/etc", "/etc/salt"], ["saltstack/srv", "/srv"]]
command = bash /vagrant/provision.sh
```

```bash
# provision.sh
if  [ ! -f "bootstrap.sh" ]; then
    echo "Updating system and installing curl"
    apt update
    apt install curl -y

    echo "Downloading Salt Bootstrap"
    curl -o bootstrap-salt.sh -L https://bootstrap.saltstack.com
fi

echo "Installing Salt with master and Python 3"
bash bootstrap-salt.sh -M -x python3

echo "Accepting the local minion's key"
salt-key -A -y


# Is Salt ready yet? Proceed once it is.
salt \* test.ping --force-color
while [ $? -ne 0 ]
do
    echo "Waiting for Salt to be up. Testing again."
    salt \* test.ping --force-color
done


echo "Running highstate. Waiting..."
salt \* state.highstate --force-color
```

That script can then be used with `rambo up`.

Alternatively, the command can be passed in the CLI, like

```bash
rambo up -c 'bash /vagrant/provision.sh'
```

Note that when this is done, keep in mind that double quotes may use shell expansion. So if

```bash
rambo up -c "echo $PWD"
```

is used with bash, the working directory _of the host_ will be echoed.
