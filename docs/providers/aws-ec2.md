# AWS EC2 Provider:

## Create Account

After you installed the dependencies on your host computer you now need to create an account at AWS.
This repo will create real resources on AWS so you need to provide AWS with valid payment and remember you might rack up a bill if you run a whole bunch of machines. You have been warned.

## Create SSH Keys

Next you need to create a ssh key pair for AWS.

Run:
```
mkdir -p auth/keys
cd auth/keys
ssh-keygen -t rsa -N '' -f "aws.pem"
xclip -sel clip < aws.pem.pub
```

*If you want multiple users or computers to access the same AWS profile or team, you must have unique key names. For example, you will need to change the base name of your `.pem` and `.pem.pub` files to something else like `aws-myname`.

**Create a new key and name the key the same as the base name of your ssh key. If AWS's key name and the one one your host don't match, you won't communicate to your VM.**

Now go to AWS's "EC2 Dashboard", on the left hand side go to "Key Pairs" and click the "Import Key Pair" button.

Here are instructions on how to setup ssh keys with aws:

http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html

**NOTE: You need the aws.pem file and the aws.pem.pub file. The aws.pem file needs permissions set to 600 and The aws.pem.pub file needs permissions set to 644**

Be careful not to commit this file to the repo. We setup this repo to ignore all files ending in `.pem`. But, you could theoretically still commit the pem file (by forcing a commit for example).
Store this pem file in a safe place with restricted access. Anyone who has this file can log into your machines on AWS and run arbitrary commands on them.

## Create Security Group

Now go to AWS's "EC2 Dashboard", on the left hand side go to "Security Group" and click the "Create Security Group" button.

Name the new security group **salted_server**.

Add these inbound rules to the security group
```
"All ICMP - IPv4", ICMP, 0 - 65535, anywhere

"SSH", TCP, 22, anywhere

"HTTP", TCP, 80, anywhere

"HTTPS", TCP, 443, anywhere

"Custom TCP Rule", TCP, 4505, anywhere

"Custom TCP Rule", TCP, 4506, anywhere

"Custom TCP Rule", TCP, 5000, anywhere

"Custom TCP Rule", TCP, 8080, anywhere

"Custom TCP Rule", TCP, 8888, anywhere
```

## Create API Token

Next you need to manually create an API access token on AWS.

Go to the "IAM Dashboard", then go to "users", now click on the user who will be creating the AWS EC2 instances. Click on the "Security Credectials" tab, click the "create access key" button.

You MUST get both the **Access key ID** and the **Secret access key**.

**NOTE: AWS will only show you this key ONCE.**

## Edit Script to Load Environment Variables

Here is the contents of the aws.env.sh file. Edit it by replacing the placeholder tags with your keys and tokens.

```
#!/bin/bash

# for aws
export AWS_ACCESS_KEY_ID=<YOUR AWS KEY ID>
export AWS_SECRET_ACCESS_KEY=<YOUR AWS ACCESS KEY>
export AWS_KEYPAIR_NAME="Vagrant"
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

## Launching Your AWS EC2 Instance
Finally, run:

```
rambo up -p ec2
rambo ssh
```
