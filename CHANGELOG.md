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
  - Now deletes broken symlinks found that would otherwise break Rambo during the rsync process.

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
