# Customizing Rambo

Rambo aims to make it easy for you to switch providers and customize provisioning. Below is documentation about how to go about cusomizing your provisioning with Salt Stack, switching provisioners, adding providers, and customizing provider-specific code.

Rambo is young, and we'd love to improve Rambo and make this all easier still. Please consider opening [a pull request](https://github.com/terminal-labs/rambo/compare) if you add another provisioner or provider, or make any customization that would be a good contribution. :)

## Custom Provisioning
Rambo provides a basic default provisioning with Vagrant and SaltStack. To build out what you need for your project you will need your own customized provisioning. You can do this provisioning with any tool you like through Vagrant, such as with shell scripts, SaltStack, or any other provisioning tool.

All Rambo code that is used to provision the VM is kept where Rambo is installed. This directory is copied into the VM at an early stage in the spawn process so that it can be invoked to provision the VM.

### SaltStack
Rambo has [a few basic Salt States](https://github.com/terminal-labs/sample-states/tree/basic) available that are placed in your project dir by `rambo createproject`. These run unless removed, and work out of the box. The `saltstack` dir can also be modified however you like for any SaltStack provisioning. You can add your custom Salt States right into the Salt code and they should be automatically picked up and used.

### Other Provisioners
If you want to add provisioning with any other tool, you will need to modify the Vagrantfiles to add that provisioning. To export the Vagrantfiles, run `rambo export-vagrant-conf` inside your project dir. This will drop the Vagrantfile and several of its dependencies. You can likely add custom provisioning straight to the main Vagrantfile without worrying about the other files.

For example, if you'd like to provision with Ansible, you will need to add custom Vagrant code to make this work. There are many useful introductions to various provisioners on Vagrant's website, such as the page on [Ansible Provisioning](https://www.vagrantup.com/docs/provisioning/ansible.html).

## Custom Providers / Provider configuration

First grab the Vagrantfiles with `rambo export-vagrant-conf`.

The main Vagrantfile is extended by other provider-specific vagrantfiles located in `vagrant/vagrantfiles` such as `vagrant/vagrantfiles/virtualbox` for VirtualBox. If you need to customize how Rambo works with a provider manually, these are the files you'll need to modify. For instance, you may want to customize many aspects of your VirtualBox VM's networking.
