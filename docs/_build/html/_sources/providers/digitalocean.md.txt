# DigitalOcean Provider:

## Create Account

After you installed the dependencies on your host computer you now need to create an account at digitalocean. 

This repo will create real resources on DigitalOcean so you need to provide DigitalOcean with valid payment and remember you might rack up a bill if you run a whole bunch of machines. You have been warned.

## Create SSH Keys

Next you need to create a ssh key pair for DigitalOcean.

Run*:
```
mkdir -p auth/keys
cd auth/keys
ssh-keygen -t rsa -N '' -f "digitalocean.pem"
xclip -sel clip < digitalocean.pem.pub
```

*If you want multiple users or computers to access the same DigitalOcean profile or team, you must have unique key names. For example, you will need to change the base name of your `.pem` and `.pem.pub` files to something else like `digitalocean-myname`.

Now go to [https://cloud.digitalocean.com/settings/security](https://cloud.digitalocean.com/settings/security) 

**Create a new key and name the key the same as the base name of your ssh key. If DigitalOcean's key name and the one one your host don't match, you won't communicate to your VM.**

Copy the contents of `digitalocean.pem.pub` into the new key field.

Here are instructions on how to setup ssh keys with DigitalOcean:

[https://www.digitalocean.com/community/tutorials/how-to-use-ssh-keys-with-digitalocean-droplets](https://www.digitalocean.com/community/tutorials/how-to-use-ssh-keys-with-digitalocean-droplets)

**NOTE: You need the `digitalocean.pem` file and the `digitalocean.pem.pub` file. The `digitalocean.pem` file needs permissions set to 600 and The `digitalocean.pem.pub` file needs permissions set to 644**

Be careful not to commit this file to the repo. We setup this repo to ignore all files ending in `.pem`. But, you could theoretically still commit the pem file (by forcing a commit for example). 
Store this pem file in a safe place with restricted access. Anyone who has this file can log into your machines on DigitalOcean and run arbitrary commands on them.

## Create API Token

Next you need to manually create an API access token on digitalocean.com 

Go to: 

[https://cloud.digitalocean.com/settings/api/](https://cloud.digitalocean.com/settings/api/)

**NOTE: DigitalOcean will only show you this key ONCE.**

Store this token in a safe place with restricted access. Anyone who has this token can create, edit, or destroy resources on digital ocean, they could rack up a huge bill for you or shut down all your vms. 

## Edit Script to Load Environment Variables

Here is the contents of the `digitalocean.env.sh` file. Edit it by replacing the placeholder tags with your key and token.

```
#!/bin/bash

# for digitalocean
export DIGITALOCEAN_TOKEN=<YOUR DIGITALOCEAN API TOKEN>
export DIGITALOCEAN_PRIVATE_KEY_PATH="auth/keys/digitalocean.pem"
```

Put your DigitalOcean API token in the line:
`export DIGITALOCEAN_TOKEN=<YOUR DIGITALOCEAN API TOKEN>`

Put the **path** to your DigitalOcean ssh private key in the line:
`export DIGITALOCEAN_PRIVATE_KEY_PATH=<PATH TO YOUR PRIVATE KEY>`

After editing, your `digitalocean.env.sh` file will look similar to this:

```
#!/bin/bash

# for digitalocean
export DIGITALOCEAN_TOKEN="0bf1d884e737417e2ea6f7a29c6035752bf8c31b366489c5366745dad62a8132"
export DIGITALOCEAN_PRIVATE_KEY_PATH="auth/keys/digitalocean.pem"
```


Note: the public key must be in the same dir as the private key and the public key must share the same base name as the private key (just append ".pub" on the public key file's name)

Now you need to source the `digitalocean.env.sh` file. cd into the repo and run:

`source digitalocean.env.sh`

## Launching Your DigitalOcean Instance
Finally, run:

```
rambo up -p digitalocean
rambo ssh
```
