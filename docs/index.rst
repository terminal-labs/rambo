Welcome to Rambo's documentation!
=================================

|Join the chat at https://gitter.im/terminal-labs/rambo|

Latest: v\ |version|

Quickstart
----------

To get started fast, see `Quickstart <docs/Quickstart>`__.

.. toctree::
   :caption: Usage Documentation
   :maxdepth: 2
   :glob:

   core/quickstart
   core/*

.. toctree::
   :caption: Provider Specific Documentation
   :maxdepth: 2
   :glob:

   providers/*

.. toctree::
   :caption: Changelog:
   :maxdepth: 1
   :glob:

   CHANGELOG

What's Rambo For?
-----------------

This project is for provisioning and configuring virtual machines (and
containers) in a simple, predictable, and highly reproducible way. Just
run one command and your VM is up, code is deployed, and your app is
running, on any supported platform.

At this time this repo allows you to create a Linux VM on multiple
providers (AWS EC2, DigitalOcean, VirtualBox, LXC). Several Operating
Systems are available on select providers. The base machine
configuration is a Ubuntu 16.04 64bit OS with 1024MB RAM, and 30GB
drive.

One of the goals of this project is be able to run a simple command and
have a new VM be created on your provider of choice. Once the VM is
initialized SaltStack is used to deploy code to and provision your
machine. The SaltStack machine configuration code (states) will run the
same regardless of which provider is actually running the machine. You
can easily cycle your VMs by destroying and rebuilding them.

Another goal of this repo is to have the spawned VMs be maximally
similar across providers. Usually, your configuration will not need to
change at all and will simply run on all providers.

By default Rambo offers a basic VM configuration with SaltStack, but you
can customize this. See `Customizing Rambo <docs/customizing>`__
for that.

Basic Usage
-----------

Once `installed <docs/quickstart/#installation>`__, you can run one of
these commands to get your VM:

for `VirtualBox <https://www.virtualbox.org/>`__ run

::

    $ rambo up
    $ rambo ssh

for `AWS EC2 <https://aws.amazon.com/ec2/>`__ run

::

    $ rambo up -p ec2
    $ rambo ssh

for `DigitalOcean <https://www.digitalocean.com/>`__ run

::

    $ rambo up -p digitalocean
    $ rambo ssh

for `Docker <https://www.docker.com/>`__ run

::

    $ rambo up -p docker
    $ rambo ssh

for `LXC <https://linuxcontainers.org/>`__ run

::

    $ rambo up -p lxc
    $ rambo ssh


Contributing
------------

We heartily welcome any contirubtions to this project, whether in the
form of commenting on or posting an issue, or development. If you would
like to submit a pull request, you might first want to look at our
development `guidlines <https://github.com/terminal-labs/rambo/blob/master/RULES.md>`__ for this project.

Special Thanks
--------------

Thanks go out to the Vagrant community and HashiCorp. Vagrant is a great
tool it has helped us a lot over the years.

Rambo is supported by `Terminal Labs`_.

.. _`Terminal Labs`: https://terminallabs.com
.. |Join the chat at https://gitter.im/terminal-labs/rambo| image:: https://badges.gitter.im/terminal-labs/rambo.svg
   :target: https://gitter.im/terminal-labs/rambo?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge
