{% set os, os_family = salt['grains.item']('os', 'os_family') %}

## Commented sections use a compiled python.
#python_install_dir:
#  file.directory:
#    - user: {{ grains['deescalated_user'] }}
#    - group: {{ grains['deescalated_user'] }}
#    - mode: 755
#    - makedirs: True
#    - name: /home/{{ grains['deescalated_user'] }}/.localpython

#python_src_dir:
#  file.directory:
#    - user: {{ grains['deescalated_user'] }}
#    - group: {{ grains['deescalated_user'] }}
#    - mode: 755
#    - makedirs: True
#    - name: /home/{{ grains['deescalated_user'] }}/.python2.7_src

#python_src_extraction:
#  archive.extracted:
#    - name: /home/{{ grains['deescalated_user'] }}/.python2.7_src/
#    - source: http://www.python.org/ftp/python/2.7.9/Python-2.7.9.tgz
#    - source_hash: md5=5eebcaa0030dc4061156d3429657fb83
#    - archive_format: tar
#    - user: {{ grains['deescalated_user'] }}
#    - if_missing: /home/{{ grains['deescalated_user'] }}/.python2.7_src/Python-2.7.9/

#python_custom_install:
#  cmd.run:
#    - cwd: /home/{{ grains['deescalated_user'] }}/.python2.7_src/Python-2.7.9/
#    - runas: {{ grains['deescalated_user'] }}
#    - unless: test -x /home/web_server/.localpython/bin/python2.7
#    - name: |
#        make clean
#        ./configure --prefix=/home/{{ grains['deescalated_user'] }}/.localpython
#        make
#        make install

python_packages:
  pkg.installed:
    - pkgs:
      - python-setuptools
      - python-virtualenv
{% if os_family == 'Debian'%}
      - python
      - python-pip
      - python-dev
      - python3
      - python3-pip
      - python3-dev
{% elif os == 'CentOS' %}
      - python
      - python2-pip
      - python-devel
      - python36u
      - python36u-pip
      - python36u-devel
{% endif %}
