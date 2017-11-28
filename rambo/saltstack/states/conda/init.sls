{% set current_path = salt['environ.get']('PATH', '/bin:/usr/bin') %}
{% set conda_path = '/home/' + grains['deescalated_user'] + '/miniconda3' %}
{% set conda_bin_path = conda_path + '/bin' %}

download_miniconda_installer:
  cmd.run:
    - name: wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /home/{{ grains['deescalated_user'] }}/miniconda.sh
    - unless: test -f {{ conda_bin_path }}/conda
    - runas: {{ grains['deescalated_user'] }}
    - require:
      - sls: users

install_miniconda:
  cmd.run:
    - name: bash miniconda.sh -b
    - unless: test -f {{ conda_bin_path }}/conda
    - runas: {{ grains['deescalated_user'] }}

add_conda_to_bashrc:
  file.append:
    - name: /home/{{ grains['deescalated_user'] }}/.bashrc
    - text:
      - export PATH={{ conda_bin_path }}:$PATH
      - source activate conda_env
    - runas: {{ grains['deescalated_user'] }}

creat_conda_env:
  cmd.run:
    - name: conda create -y --name conda_env pip
    - runas: {{ grains['deescalated_user'] }}
    - env:
      - PATH: {{ [current_path, conda_bin_path]|join(':') }}
