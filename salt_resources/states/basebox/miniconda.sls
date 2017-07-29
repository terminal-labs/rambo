download_miniconda_installer:
  cmd.run:
    - name: wget http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh -O /home/vagrant/miniconda.sh
    - unless: test -f /usr/local/bin/miniconda/bin/conda

ensure_miniconda_is_installed:
  cmd.run:
    - name: bash /home/vagrant/miniconda.sh -b -p /usr/local/bin/miniconda
    - unless: test -f /usr/local/bin/miniconda/bin/conda
