# Environment Variables

**This is advanced and shouldn't be used without good reason.**

Like the config file, options can also be specified as environment variables. However, this is much more complex, and we strongly recommend not using these manually, as we think it's much easier to lose track of what's going on and cause undue headache.

Most env vars are prefixed with `RAMBO_` in an attempt to make them easy to visually pick out, and unlikely to conflict with other env vars used by your shell session. After this prefix is the name of each CLI option, in all caps, with dashes replaced by underscores, e.g. `RAMBO_GUEST_OS`. This form covers most env vars, the exception being env vars that Rambo needs to set that are used by Vagrant directly. In this case we cannot change the name of the env var, and must use Vagrant's. For example, Rambo uses (and you can set) [`VAGRANT_DOTFILE_PATH`](https://www.vagrantup.com/docs/other/environmental-variables.html#vagrant_dotfile_path) and [`VAGRANT_CWD`](https://www.vagrantup.com/docs/other/environmental-variables.html#vagrant_cwd). All of these CLI-related env vars can be set in the shell session, and will be picked up and used by Rambo if those same options are not otherwise set. Both the `rambo.conf` file and options set within the CLI take precedence over env vars. The precedence is thus CLI > Config > Env Var > defaults.
