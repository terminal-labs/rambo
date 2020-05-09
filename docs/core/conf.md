# rambo.conf

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

The `rambo.conf` file is required at the top level in your project directory. It is an INI config file that can specify options. Options passed to the CLI will take precedence over options set via this config file. If you're repeating the same CLI options, setting those options in this config might make your life a little easier. Further, if you intend on tracking your Rambo project in version control, it can be very handy to set some options in this config that match the purpose of your project.

Options can be set in `rambo.conf`. For example, a useful `rambo.conf` could look like this:

```ini
[up]
provider = digitalocean
guest_os = centos-7
```

which is equivalent to:

```bash
rambo up --provider digitalocean --guest-os centos-7
```

Setting the config file to this allows you to type simply `rambo up` to run `up` with the `provider` and `guest-os` options set in the rambo.conf, and not specified in the CLI.

## Option Names

The options in the conf file are the same as the full option names in the CLI, with preceeding dashes removed and other dashes replaced with underscores. As examples:

- `vagrant_dotfile_path` in the conf, corresponds to `--vagrant-dotfile-path` in the CLI
- `provider` in the conf, corresponds to `--provider` or `-p` in the CLI
- `guest_os` in the conf, corresponds to `--guest-os` or `-o` in the CLI
- `ram_size` in the conf, corresponds to `--ram-size` or `-r` in the CLI

The full list is available with `rambo up --help`.

## my_rambo.conf

Rambo will also load configuration from a `my_rambo.conf` file. This file is optional, and configuration found here takes precedence over the main `rambo.conf` file.

The intention is that a `rambo.conf` file is tracked (e.g. with git), but so that a shared project can have its configuration easily altered by individual users, values may be overridden by an untracked `my_rambo.conf`. For example, a project may use `provider = ec2`, but individual contributors may want to develop locally in Docker or VirtualBox instead.

## Option Precedence

The precedence for options is:

CLI > Environment Variable > `my_rambo.conf` > `rambo.conf` > defaults

When an option is set in more than one place, the CLI takes precedence. Defaults are overridable by everything.

### Example 1

```ini
# rambo.conf

[up]
provider = digitalocean
```

```bash
rambo up -p virtualbox
```

yields the provider `virtualbox`.

### Example 2

If instead, the config still read

```ini
# rambo.conf

[up]
provider = digitalocean
```

```bash
rambo up
```

yields the provider `digitalocean`.

### Example 3

```bash
RAMBO_PROVIDER=digitalocean rambo up -p ec2
```

yields the provider `ec2`.

### Example 4

```ini
# rambo.conf

[up]
provider = ec2
```

```bash
RAMBO_PROVIDER=digitalocean rambo up
```

yields the provider `digitalocean`.

### Example 4

```ini
# my_rambo.conf

[up]
provider = virtualbox
```

```ini
# rambo.conf

[up]
provider = ec2
```

yields the provider `virtualbox`.
