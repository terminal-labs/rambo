## 0.2.2 (TBD)

FEATURES:

  - Added a Salt state for Hadoop Ambari.
  - Added basic network modifications for clustering.
  - Setting the hostname to the VM_NAME.

IMPROVEMENTS:

  - Now enforcing Vagrant >=1.9.7.
  - VM_NAME now contains host's hostname, and rambo's working dir, and a unique hex id.

BUG FIXES:

  - Fix ability to set repository branch and then execute highstate.

## 0.2.1 (August 9, 2017)

FEATURES:

  - Now activating conda environment upon `vagrant ssh`.
  - Added Salt State for Anaconda.
  - Added Salt State for loading a database dump from a local store, and
    allowing using this or the artifacts state.

IMPROVEMENTS:

  - Added default fingerprints for BitBucket and GithHub.
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
