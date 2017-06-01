# **Installation**

## Setup

### Hardware Recommendations
For running vms locally in VirtualBox

* Reasonably fast cpu with 2 or more cores and VT-x (I used a Intel i7-3612QM 2.1GHz, 4 core chip)
* 8gb ram (or more)
* 16gb free drive space  (or more)

For running containers in lxc locally or spawning machine in aws/digitalocean you can get away with comparatively slow computer and you don't need VT-x. In fact, the LXC/EC2/DigitalOcean providers can be managed from a Raspberry Pi. See: https://www.raspberrypi.org/

### Summary of Setup:
You need to install some programs into your host, then you will need to install some Vagrant plugins. You also need to setup full accounts (or login into existing accounts) at DigitalOcean and AWS.

### Supported OS:
[Ubuntu 16.04 or newer](https://www.ubuntu.com/download/desktop)

[OSX](http://www.apple.com/mac-mini/)

### Dependencies (Ubuntu):
You first need to install some dependencies via app: run

```
#!bash
sudo apt install -y build-essential linux-headers-$(uname -r) lxc lxc-templates cgroup-lite redir xclip
```

Then install your correct Deb packages:

[Vagrant 1.9.2 or newer](http://www.vagrantup.com/)

[VirtualBox 5.1 or newer](https://www.virtualbox.org/)

Note: Vagrant and VirtualBox update frequently, and sometimes with breaking changes.

### Dependencies (Mac):
For OS X installing 2 dmg files should be all you need

[Vagrant 1.9.2 or newer](http://www.vagrantup.com/)

[VirtualBox 5.1 or newer](https://www.virtualbox.org/)

Note: Vagrant and VirtualBox update frequently, and sometimes with breaking changes.

### Install Vagrant plugins: ###
cd into the `rambo` repo and run:

```
#!bash
bash setup.sh
```

## **Working with VirtualBox Provider:**

Assuming that you installed the dependencies you should be able to run 

`vagrant up`

or the more verbose command 

`vagrant --target=virtualbox up`

## **Working with AWS EC2 Provider:**

### Create Account

After you installed the dependencies on your host computer you now need to create an account at AWS.
This repo will create real resources on AWS so you need to provide AWS with valid payment and remember you might rack up a bill if you run a whole bunch of machines. You have been warned.

### Create SSH Keys

Next you need to create a ssh key pair for AWS.

Run:
```
#!bash
mkdir -p auth/keys
cd auth/keys
ssh-keygen -t rsa -N '' -f "aws.pem"
xclip -sel clip < aws.pem.pub
```

Now go to AWS's "EC2 Dashboard", on the left hand side go to "Key Pairs" and click the "Import Key Pair" button.

**Create a new key and name the key "Vagrant". Copy the contents of aws.pem.pub into the new key field.

Here are instructions on how to setup ssh keys with aws:

http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html

**NOTE: You need the aws.pem file and the aws.pem.pub file. The aws.pem file needs permissions set to 600 and The aws.pem.pub file needs permissions set to 644**

Be careful not to commit this file to the repo. We setup this repo to ignore all files ending in `.pem`. But, you could theoretically still commit the pem file (by forcing a commit for example). 
Store this pem file in a safe place with restricted access. Anyone who has this file can log into your machines on AWS and run arbitrary commands on them.

### Create Security Group

Now go to AWS's "EC2 Dashboard", on the left hand side go to "Security Group" and click the "Create Security Group" button.

Name the new security group **salted_server**. 

Add these inbound rules to the security group
```
#!bash
"HTTP", TCP, 80, anywhere

"SSH", TCP, 22, anywhere

"Custom TCP Rule", TCP, 4506, anywhere

"Custom TCP Rule", TCP, 4505, anywhere

"HTTPS", TCP, 443, anywhere

"All ICMP - IPv4", ICMP, 0 - 65535, anywhere
```

### Create API Token

Next you need to manually create an API access token on AWS.

Go to the "IAM Dashboard", then go to "users", now click on the user who will be creating the AWS EC2 instances. Click on the "Security Credectials" tab, click the "create access key" button.

You MUST get both the **Access key ID** and the **Secret access key**.

**NOTE: AWS will only show you this key ONCE.**

### Edit Script to Load Environment Variables

Here is the contents of the aws.env.sh file. Edit it by replacing the placeholder tags with your keys and tokens.

```
#!/bin/bash

# for aws
export AWS_ACCESS_KEY_ID=<YOUR AWS KEY ID>
export AWS_SECRET_ACCESS_KEY=<YOUR AWS ACCESS KEY>
export AWS_KEYPAIR_NAME="aws"
export AWS_SSH_PRIVKEY="auth/keys/aws.pem"
```

Put your aws access key token in the line:
`export AWS_ACCESS_KEY_ID=<YOUR AWS KEY ID>`

Put your aws secret acces key token in the line:
`export AWS_SECRET_ACCESS_KEY=<YOUR AWS ACCESS KEY>`

Put the **name** of your aws ssh private key in the line:
`export AWS_KEYPAIR_NAME="aws"`

Put the **path** to your aws ssh private key in the line:
`export AWS_SSH_PRIVKEY="auth/keys/aws.pem"`

After editing, your aws.env.sh file will look similar to this:

```
#!/bin/bash

# for aws
export AWS_ACCESS_KEY_ID="AKIAITT673DAF4YNV7MA"
export AWS_SECRET_ACCESS_KEY="m25AyjXtiYB2cCWMv1vQeyZtWqiWg0nqxi2Wm2QX"
export AWS_KEYPAIR_NAME="aws"
export AWS_SSH_PRIVKEY="auth/keys/aws.pem"
```

Note: the public key must be in the same dir as the private key and the public key must share the same base name as the private key (just append ".pub" on the public key file's name).

Now you need to source the aws.env.sh file. cd into the repo and run:

`source aws.env.sh`

### Launching Your AWS EC2 Instance
Finally, run:

```
#!bash
vagrant --target=ec2 up
vagrant ssh
```

## **Working With DigitalOcean Provider:**

### Create Account

After you installed the dependencies on your host computer you now need to create an account at digitalocean. 

This repo will create real resources on DigitalOcean so you need to provide DigitalOcean with valid payment and remember you might rack up a bill if you run a whole bunch of machines. You have been warned.

### Create SSH Keys

Next you need to create a ssh key pair for DigitalOcean.

Run:
```
#!bash
mkdir -p auth/keys
cd auth/keys
ssh-keygen -t rsa -N '' -f "digitalocean.pem"
xclip -sel clip < digitalocean.pem.pub
```

Now go to [https://cloud.digitalocean.com/settings/security](https://cloud.digitalocean.com/settings/security) 

**Create a new key and name the key "Vagrant". The key MUST be named "Vagrant".** Copy the contents of digitalocean.pem.pub into the new key field.

Here are instructions on how to setup ssh keys with DigitalOcean:

[https://www.digitalocean.com/community/tutorials/how-to-use-ssh-keys-with-digitalocean-droplets](https://www.digitalocean.com/community/tutorials/how-to-use-ssh-keys-with-digitalocean-droplets)

**NOTE: You need the digitalocean.pem file and the digitalocean.pem.pub file. The digitalocean.pem file needs permissions set to 600 and The digitalocean.pem.pub file needs permissions set to 644**

Be careful not to commit this file to the repo. We setup this repo to ignore all files ending in `.pem`. But, you could theoretically still commit the pem file (by forcing a commit for example). 
Store this pem file in a safe place with restricted access. Anyone who has this file can log into your machines on digital ocean and run arbitrary commands on them.

### Create API Token

Next you need to manually create an API access token on digitalocean.com 

Go to: 

[https://cloud.digitalocean.com/settings/api/](https://cloud.digitalocean.com/settings/api/)

**NOTE: DigitalOcean will only show you this key ONCE.**

Store this token in a safe place with restricted access. Anyone who has this token can create, edit, or destroy resources on digital ocean, they could rack up a huge bill for you or shut down all your vms. 

### Edit Script to Load Environment Variables

Here is the contents of the digitalocean.env.sh file. Edit it by replacing the placeholder tags with your key and token.

```
#!/bin/bash

# for digitalocean
export DIGITALOCEAN_TOKEN=<YOUR DIGITALOCEAN API TOKEN>
export DIGITALOCEAN_PRIVATE_KEY_PATH="auth/keys/digitalocean.pem"
```

Put your DigitalOcean API token in the line:
`export DIGITALOCEAN_TOKEN=<YOUR DIGITALOCEAN API TOKEN>`

Put the **path** to your Digitalocean ssh private key in the line:
`export DIGITALOCEAN_PRIVATE_KEY_PATH=<PATH TO YOUR PRIVATE KEY>`

After editing, your digitalocean.env.sh file will look similar to this:

```
#!/bin/bash

# for digitalocean
export DIGITALOCEAN_TOKEN="0bf1d884e737417e2ea6f7a29c6035752bf8c31b366489c5366745dad62a8132"
export DIGITALOCEAN_PRIVATE_KEY_PATH="auth/keys/digitalocean.pem"
```


Note: the public key must be in the same dir as the private key and the public key must share the same base name as the private key (just append ".pub" on the public key file's name)

Now you need to source the digitalocean.env.sh file. cd into the repo and run:

`source digitalocean.env.sh`

### Launching Your Digitalocean Instance
Finally, run:

```
#!bash
vagrant --target=digitalocean up
vagrant ssh
```

## **Working With LXC Provider:**

**NOTE: This will only work on Ubuntu 16.04 or newer**

Assuming that you installed the dependencies and that you are running Ubuntu16.04+ as your host you should be able to run

```
#!bash
vagrant --target=lxc up
vagrant ssh
```
