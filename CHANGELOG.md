# Changelog

## TBD

FEATURES:

- Add option to set path to sync into VM.
- Add option to provision from script with path.
- Add option to start provisioning with command.
- Add option to set VM name.
- Add option to set hostname.
- Add option to set cpus in virtualbox.
- Add option to set sync_type and defauting to Vagrant's default.
- Add option to provision with Salt.
- Add option to set salt-bootstrap args.
- Add option to sync all listed dirs.
- Add optional setting overrides with my_rambo.conf.
- Add option to resize base VirtualBox drive size with vagrant plugin.
- Add option to set ports that are forwarded.

IMPROVEMENTS:

- `rambo destroy` will now use vboxmanage to fully poweroff and delete VirtualBox VMs.
- No longer using any custom sources.list.
- Renamed sync_dir to project_dir.
- Now you can pass fancy pathing like `..` and symlinks to the CLI.
- More comprehensive logging.
- Splitting expected saltstack dir into saltstack/etc and saltstack/srv to more easily work with the common pattern of having Salt code in /etc/salt and /srv.
- Left legacy style salt provisioning, but added a flag to use it instead of the newer style.

BUGFIXES:

- Fix bug incorrectly setting cwd, leading to nested temp dirs.
- Passes provider explicitly as cmd arg to Vagrant.
- Fixes guest hostname generation when given underscores in the path, casting it to "95", it's ascii code.
- Fixes guest hostname generation when too long, truncating the part preceding the hash so total length stays below 64 chars.
- Fix bug when setting machine-type.
- Fix ability to set cwd.

## 0.4.4 (March 9, 2018)

BUGFIX:

- Now custom fork of click_configfile is added as a submodule so it's always present, and included this in the MANIFEST.

## 0.4.0 (March 9, 2018)

FEATURES:

- Added Ubuntu Dockerfile.
- Added machine-type option for various cloud providers.
- Added ramsize and drivesize options.
- Added ability to load options via rambo.conf.
- Added `createproject` cmd to create project dir, including default
  saltstack code, auth dir, and mandatory rambo.conf.
- Added `install-plugins` cmd for installing vagrant plugins.
- Refactored shell invocation of Vagrant to ouput near real-time stdout
  and stderr, keeps ANSI formatting, stderr and exit status passthrough.
- Better logging of shell invocation of Vagrant.
- Added the ability to custom saltstack code dir that is automatically used.
- Added the ability to custom Vagrantfile that is automatically used.
- Added export-vagrant-conf cmd for dropping vagrant files for customization.
- Added option for guest os.

IMPROVEMENTS:

- Rounded out OS whitelist: Debian 8/9, CentOS 7, Ubuntu 14.04/16.04
- Fix Docker bugs
- Added readthedocs.
- Defining a project by the existence of a conf file.
- Remove support for using env vars and api simultaneously.
- If no saltstack dir is in a the project dir, no salt is run.
- Saltstack files moved to terminal-labs/sample-states repo.
  The 'basic' branch is pulled and used.
- Added in vagrantfile setting kind of syncing.
- Added toggle in vagrantfile for grabbing canonical apt sources or not
  since some images come with different, unreliable sources.
- Renamed `vagrant_resources` to `vagrant`, and `salt_resources` to `saltstack`.
- Changed default guest os from Debian 8 to Ubuntu 16.04.

## 0.3.3 (November 28, 2017)

FEATURES:

- Added ubuntu 14.04 to hosts list.

IMPROVEMENTS:

- Add version cli option.

## 0.3.2 (November 27, 2017)

FEATURES:

- Added additional Salt states for Hadoop edgenode and worker.
- Allowing setting custom tmpdir path.

IMPROVEMENTS:

- Using standard get/set_env_var_rb functions.
- Change VM_SIZE to RAMBO_RAM and created RAMBO_DRIVESIZE.
- Changed VM_Host to RAMBO_GUEST_OS.
- Cleaned up some Vagrant code.

BUG FIXES:

- Stop setting a default apt source on CentOS.
- Stop setting hostname on CentOS. Another ticket was made for that.
- Passing ctx to ssh and destroy commands.
- Changed name of base box according to the box name change on
  app.vagrantup.com for the default Debian box.

## 0.3.1 (November 8, 2017)

FEATURES:

- Now AWS makes use of VM_Size flag to produce t2.nano, t2.micro, and t2.small VMs.

IMPROVEMENTS:

- Updated docs for CLI, Python API, Environment Variables
- Renamed tmp dir to rambo-tmp.

BUG FIXES:

- `rambo destroy` now finds and deletes metadata in tmp dir.
- Fix Docker failing on editing non-existant bashrc. Now ensuring existence first.
- Fixing vagrant up exit trigger when VM not named 'default'.
- Fixed bug preventing provisioning without Salt.

## 0.3.0 (October 26, 2017)

FEATURES:

- Added Salt states to apply Anaconda licenses.
- Adding a Python API.
- Added Nano to base Salt provisioning.
- Able to set Vagrant environment variables via the CLI
- Refactored packaging for PyPI.
- Added in support for Ubuntu 14.04 and Centos 7 guest OSs.
- Added in 4GB and 8GB RAM for all supported OSs.
- Added Salt states for setting up licensed Anaconda.
- Made Rambo a pip installable package.
- Created a Python based CLI for Rambo.
- Added support for multiple users on DigitalOcean.
- Added a Salt state for Hadoop Ambari.
- Added basic network modifications for clustering.
- Setting the hostname to the VM_NAME.

IMPROVEMENTS:

- Now downloading base vagrant boxes from vagrantup.com.
- Now enforcing Vagrant >=1.9.7.
- VM_NAME now contains host's hostname, and rambo's working dir, and a unique hex id.
- Now deletes broken symlinks found that would otherwise break Rambo
  during the rsync process.

BUG FIXES:

- Fix ability to set repository branch and then execute highstate.

## 0.2.1 (August 9, 2017)

FEATURES:

- Now activating conda environment upon `vagrant ssh`.
- Added Salt State for Anaconda.
- Added Salt State for loading a database dump from a local store, and
  allowing using this or the artifacts state.

IMPROVEMENTS:

- Added default fingerprints for BitBucket and GitHub.
- Renamed miniconda state to conda.
- Added documentation for Docker provider.

BUG FIXES:

- Fixed misnamed reference to Miniconda state.
- Now requiring artifacts grains before trying to load a database.
- Deduping state IDs for adding fingerprints for git and hg.
- Specifying fingerprint hash type since that's now required by a Salt update.
- Deduping state IDs for installing pip requirements with conda and venv.
- Removing unused salt state directory.
- Bumped required vagrant version.

## 0.2.0 (August 3, 2017)

FEATURES:

- Added a Salt State for Miniconda.
- Added Docker as a provider.

IMPROVEMENTS:

- Using Packer made base boxes for VirtualBox.
- Now using paravirtualization with VirtualBox for increased speed.
- Enhanced documentation and helper markdown files.
- Renamed 'AWS' provider to 'EC2' to avoid future confusion.
- Updated documentation.
- Some code cleaning.

BUG FIXES:

- Changed the standard AWS EC2 size to t2.micron.

## 0.1.0 (May 22, 2017)

FEATURES:

- Initial commit.

The changelog began with open sourcing Rambo at version 0.1.0.
