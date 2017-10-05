install_lastpass ="""
#!/usr/bin/env bash

mkdir -p build
cd build
git clone https://github.com/lastpass/lastpass-cli.git
cd lastpass-cli
cmake . && make
"""
