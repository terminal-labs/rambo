su -m vagrant <<'EOF'
  cd /vagrant
  mkdir -p .tmp
  cd .tmp
  wget https://github.com/terminal-labs/python-environment-manager/archive/master.zip
  unzip master.zip
EOF