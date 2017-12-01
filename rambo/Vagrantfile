# -*- mode: ruby -*-
# vi: set ft=ruby :
#
# This file is meant to contain vars that are most likely to be changed
# when configuring Rambo. Further logic is loaded with a Vagrantfile for a specific provider (e.g. ec2, lxc).

require "json"

# Change CWD for each VM, as set by Rambo, otherwise relative path resources break.
if ENV.has_key?("VAGRANT_CWD")
  Dir.chdir ENV["VAGRANT_CWD"]
end

require_relative "vagrant/modules.rb" # for random_tag

## Default Settings
SETTINGS = JSON.parse(File.read('settings.json'))
PROJECT_NAME = SETTINGS["PROJECT_NAME"]
VM_NAME = PROJECT_NAME + "-" + random_tag()
FORWARD_SSH = true
CUSTOM_PKG_SRC = true
PROVISION_WITH_SALT = true
PROVISION_WITH_CMD = false
unless get_env_var_rb('SYNC')
  set_env_var_rb('SYNC', 'rsync')
end
unless get_env_var_rb('cwd')
  set_env_var_rb('cwd', Dir.pwd)
end

unless get_env_var_rb("ENV")
  puts "", "***CAUTION***",
       "Running Vagrant directly and without %s's official CLI." % PROJECT_NAME.capitalize,
       "This is not supported.",
       "***/CAUTION***", ""
end

Vagrant.require_version ">= 1.9.7"

orphan_links = `find . -xtype l`.split(/\n+/)
for link in orphan_links
  puts "Deleting broken symlink #{link}"
  File.delete(link)
end

#load the rest of the vagrant ruby code
provider = if get_env_var_rb("PROVIDER")
           get_env_var_rb("PROVIDER")
         elsif read_provider_file()
           read_provider_file()
         else
           'virtualbox'
         end

if (SETTINGS["PROVIDERS"].include? provider)
  write_provider_file(provider)
  load File.expand_path("vagrant/vagrantfiles/" + provider)
else # Bad arg - we don't have this provider.
  abort("ABORTED - Provider not in providers list. Did you have a typo?")
end

hosts = ['debian-8',
         'ubuntu-1404',
         'ubuntu-1604',
         'centos-7',
        ]

unless get_env_var_rb("GUEST_OS")
  set_env_var_rb("GUEST_OS", "debian-8")
end

unless (hosts.include? get_env_var_rb("GUEST_OS"))
   abort("ABORTED - VM host not in host list. Did you have a typo?")
end

sizes = {'512' => '20gb',
         '1024' => '30gb',
         '2048' => '40gb',
        }

unless get_env_var_rb("RAM")
  set_env_var_rb("RAM", "1024")
end

set_env_var_rb("DRIVESIZE",sizes[get_env_var_rb("RAM")])

unless (sizes.include? get_env_var_rb("RAM"))
   abort("ABORTED - VM size not in sizes list. Did you have a typo?")
end

custom_code_dirs = [
  'ansible',
  'chef',
  'puppet',
  'saltstack',
  'shell',
  'vagrant',
]

# Provisioning
Vagrant.configure("2") do |config|
  if get_env_var_rb('SYNC') != 'disabled'
    config.vm.synced_folder '.', "/vagrant", type: get_env_var_rb('SYNC')
    for custom_code_dir in custom_code_dirs
      if Dir.exist?(File.join(get_env_var_rb("CWD"), custom_code_dir))
        config.vm.synced_folder File.join(get_env_var_rb("CWD"), custom_code_dir),
          File.join("/vagrant", custom_code_dir), type: get_env_var_rb('SYNC')
      end
    end
  else # Disable all syncing. Breaks default method of provisioning.
    config.vm.synced_folder get_env_var_rb("CWD"), "/vagrant", disabled: true
  end
  if CUSTOM_PKG_SRC == true
    config.vm.provision "shell",
      inline: "if [ -f /etc/apt/sources.list ]; then wget -O /etc/apt/sources.list https://raw.githubusercontent.com/terminal-labs/package-sources/master/" + get_env_var_rb("GUEST_OS") + "/official/sources.list; fi",
      keep_color: true
  end
  if PROVISION_WITH_SALT
    config.vm.provision :salt do |salt|
      salt.bootstrap_options = "-P"
      salt.verbose = true
    end
    # Bash to set prepare and initiate Salt provisioning.
    $salt = <<-EOS
      mv /etc/salt/minion{,-dist}
      cp /vagrant/saltstack/minions/minion.#{provider}  /etc/salt/minion
      cp /vagrant/saltstack/grains/grains /etc/salt/grains
      mkdir -p /vagrant/saltstack/states/files/licenses
      if [ -d "/vagrant/auth/licenses/" ]; then
          cp -a /vagrant/auth/licenses/. /vagrant/saltstack/states/files/licenses/
      fi
      if [ #{ENV["WEBSITE_BRANCH"]} ]; then
          sudo SSH_AUTH_SOCK=$SSH_AUTH_SOCK salt-call --local grains.setval WEBSITE_BRANCH #{ENV["WEBSITE_BRANCH"]} --log-level info
      fi
      sudo SSH_AUTH_SOCK=$SSH_AUTH_SOCK salt-call --local grains.setval hostname #{VM_NAME} --log-level info
      sudo SSH_AUTH_SOCK=$SSH_AUTH_SOCK salt-call --local state.highstate --log-level info
      EOS
    config.vm.provision "shell",
      inline: $salt,
      keep_color: true
  end
  if PROVISION_WITH_CMD
    config.vm.provision "shell",
      inline: "", # TODO: Pass in path to bash file as cli arg
      keep_color: true
  end
end

# clean up files on the host after the guest is destroyed
Vagrant.configure("2") do |config|
  config.trigger.after :destroy do
    puts "Vagrant done with destroy."
  end
end
