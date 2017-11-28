{% set current_path = salt['environ.get']('PATH', '/bin:/usr/bin') %}
{% set conda_path = '/home/' + grains['deescalated_user'] + '/miniconda3' %}
{% set conda_bin_path = conda_path + '/bin' %}

install_anaconda:
  cmd.run:
    - name: conda install -y anaconda
    - runas: {{ grains['deescalated_user'] }}
    - env:
      - PATH: {{ [current_path, conda_bin_path]|join(':') }}
    - require:
      - sls: conda
