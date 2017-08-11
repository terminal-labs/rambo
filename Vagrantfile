# -*- mode: ruby -*-
# vi: set ft=ruby :
#
# This file is meant to contain vars that are most likely to be changed
# when configuring Rambo. Further logic is loaded with vagrant/core, and
# then a Vagrantfile for a specific provider (e.g. Vagrantfile.ec2).

require 'getoptlong'

load "vagrant_resources/modules.rb" # for random_tag

Vagrant.require_version ">= 1.9.7"

opts = GetoptLong.new(
  # Native Vagrant options
  [ '--force', '-f', GetoptLong::NO_ARGUMENT ],
  [ '--provision', '-p', GetoptLong::NO_ARGUMENT ],
  [ '--provision-with', GetoptLong::NO_ARGUMENT ],
  [ '--provider', GetoptLong::OPTIONAL_ARGUMENT ],
  [ '--help', '-h', GetoptLong::NO_ARGUMENT ],
  [ '--check', GetoptLong::NO_ARGUMENT ],
  [ '--logout', GetoptLong::NO_ARGUMENT ],
  [ '--token', GetoptLong::NO_ARGUMENT ],
  [ '--disable-http', GetoptLong::NO_ARGUMENT ],
  [ '--http', GetoptLong::NO_ARGUMENT ],
  [ '--https', GetoptLong::NO_ARGUMENT ],
  [ '--ssh-no-password', GetoptLong::NO_ARGUMENT ],
  [ '--ssh', GetoptLong::NO_ARGUMENT ],
  [ '--ssh-port', GetoptLong::NO_ARGUMENT ],
  [ '--ssh-once', GetoptLong::NO_ARGUMENT ],
  [ '--host', GetoptLong::NO_ARGUMENT ],
  [ '--entry-point', GetoptLong::NO_ARGUMENT ],
  [ '--plugin-source', GetoptLong::NO_ARGUMENT ],
  [ '--plugin-version', GetoptLong::NO_ARGUMENT ],
  [ '--debug', GetoptLong::NO_ARGUMENT ],
  
  # custom options 
  [ '--target', GetoptLong::OPTIONAL_ARGUMENT ],
)

VM_NAME = "rambo-" + random_tag()

VM_SIZE = "1024mb"

FORWARD_SSH = true

COPY_DIR_WITH_RSYNC = true

PROVISION_WITH_SALT = true

PROVISION_WITH_CMD = true

## Construct commands to have Salt provision the machine.# Pass var to allow Salt to set the hostname to the VM_NAME.
SET_HOSTNAME = "sudo SSH_AUTH_SOCK=$SSH_AUTH_SOCK salt-call --local grains.setval hostname " + VM_NAME + " --log-level info; "

# Set hostname + run highstate.
PROVISION_CMD = SET_HOSTNAME + "sudo SSH_AUTH_SOCK=$SSH_AUTH_SOCK salt-call --local state.highstate --log-level info"

# Add website branch var if applicable.
if ENV["WEBSITE_BRANCH"]
  PROVISION_CMD = "sudo SSH_AUTH_SOCK=$SSH_AUTH_SOCK salt-call --local grains.setval WEBSITE_BRANCH " + ENV["WEBSITE_BRANCH"] + " --log-level info; " + PROVISION_CMD
end

#load the rest of the vagrant ruby code
load File.expand_path("vagrant_resources/vagrant/core")
