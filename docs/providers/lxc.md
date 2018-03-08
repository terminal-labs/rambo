# LXC

**NOTE: At this time, this will only work on Ubuntu 16.04+ host OS**

At this time LXC is supported natively on Ubuntu 16.04. For this native support, you need a few additional dependencies. They can all be installed with this:

```
sudo apt install -y build-essential linux-headers-$(uname -r) lxc lxc-templates cgroup-lite redir
```

After that, starting an LXC container with basic usage is:

```
rambo up -p lxc
rambo ssh
```

**Note:** At this time using LXC as a provider will require root priveleges / sudo.
