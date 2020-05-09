# Basic Provisioning

By default Rambo will do a small amount of basic provisioning. It will:

- Set the hostname
- Sync your project directory
- Sync additinoal configuration file directories
- Sync custom directories

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

Rambo will look for and sync directories that are commonly used for provisioning, and may optionally sync additional specified directories. The following mappings are synced in the order listed.

| Host (source)                   | VM (target)           |
|---------------------------------|-----------------------|
| [ project dir]                  | /vagrant              |
| [ project dir]/saltstack/srv    | /srv                  |
| [ project dir]/saltstack/etc    | /etc/salt             |
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
