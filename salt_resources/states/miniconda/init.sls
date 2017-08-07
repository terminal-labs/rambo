{% set current_path = salt['environ.get']('PATH', '/bin:/usr/bin') %}
{% set miniconda_path = '/usr/local/bin/miniconda/bin' %}

download_miniconda_installer:
  cmd.run:
    - name: wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /home/{{ grains['deescalated_user'] }}/miniconda.sh
    - unless: test -f {{ miniconda_path }}/conda
    - runas: {{ grains['deescalated_user'] }}

ensure_miniconda_is_installed:
  cmd.run:
    - name: bash /home/{{ grains['deescalated_user'] }}/miniconda.sh -b -p /usr/local/bin/miniconda
    - unless: test -f {{ miniconda_path }}/conda

add_conda_to_bashrc:
  file.append:
      - name: /home/{{ grains['deescalated_user'] }}/.bashrc
      - text:
        - export PATH={{ miniconda_path }}:$PATH
        - source activate miniconda_env
      - runas: {{ grains['deescalated_user'] }}
      - require:
        - sls: users

creat_miniconda_env:
  cmd.run:
    - name: conda create -y --name miniconda_env pip
    - runas: {{ grains['deescalated_user'] }}
    - env:
      - PATH: {{ [current_path, miniconda_path]|join(':') }}
