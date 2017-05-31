# -*- mode: ruby -*-
# vi: set ft=ruby :
#
# This file is meant to contain vars that are most likely to be changed
# when configuring Rambo. Further logic is loaded with vagrant/core, and
# then a Vagrantfile for a specific provider (e.g. Vagrantfile.aws-ec2).

require 'getoptlong'

load "vagrant_resources/modules.rb" # for random_tag

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

if ENV["WEBSITE_BRANCH"]
  PROVISION_CMD = "sudo SSH_AUTH_SOCK=$SSH_AUTH_SOCK salt-call --local grains.setval WEBSITE_BRANCH " + ENV["WEBSITE_BRANCH"] + " --log-level info"
else
  PROVISION_CMD = "sudo SSH_AUTH_SOCK=$SSH_AUTH_SOCK salt-call --local state.highstate --log-level info"
end

#load the rest of the vagrant ruby code
load File.expand_path("vagrant_resources/vagrant/core")
