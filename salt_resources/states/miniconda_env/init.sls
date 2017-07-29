{% set current_path = salt['environ.get']('PATH', '/bin:/usr/bin') %}
{% set miniconda_path = '/usr/local/bin/miniconda/bin' %}

creat_miniconda_env:
  cmd.run:
    - name: conda create -y --name miniconda_env pip
    - runas: vagrant
    - env:
      - PATH: {{ [current_path, miniconda_path]|join(':') }}
