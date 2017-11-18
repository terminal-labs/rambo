#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ -d $DIR/auth/env_scripts/digitalocean.env.sh.dist ]; then cp $DIR/auth/env_scripts/digitalocean.env.sh.dist digitalocean.env.sh; fi
if [ -d $DIR/auth/env_scripts/aws.env.sh.dist ]; then cp $DIR/auth/env_scripts/aws.env.sh.dist aws.env.sh; fi

vagrant plugin install vagrant-aws
vagrant plugin install vagrant-digitalocean
vagrant plugin install vagrant-lxc
vagrant plugin install vagrant-triggers
vagrant plugin install vagrant-scp
