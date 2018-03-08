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

## Option Precedence

When an option is set in both places, the CLI takes precedence. For example, if the `provider` is set to `digitalocean` in the config:

```ini
[up]
provider = digitalocean
```

and `virtualbox` in the CLI

```bash
rambo up -p virtualbox
```

then `virtualbox` would take precedence and be the provider that is used. If instead, the config still read

```ini
[up]
provider = digitalocean
```

and no provider was specified in the CLI, as in

```bash
rambo up
```

then the provider `digitalocean` would be used, because the config file takes precedence over the default value `virtualbox`, but no explicit value is given in the CLI.

The precedence is CLI > Config > defaults.
