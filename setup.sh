#!/usr/bin/env bash
cp auth/env_scripts/digitalocean.env.sh.dist digitalocean.env.sh
cp auth/env_scripts/aws.env.sh.dist aws.env.sh

vagrant plugin install vagrant-aws
vagrant plugin install vagrant-digitalocean
vagrant plugin install vagrant-lxc
vagrant plugin install vagrant-triggers
vagrant plugin install vagrant-scp
