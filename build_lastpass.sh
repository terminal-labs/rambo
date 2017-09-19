#!/usr/bin/env bash

git clone https://github.com/lastpass/lastpass-cli.git
cd lastpass-cli
cmake . && make
sudo make install
