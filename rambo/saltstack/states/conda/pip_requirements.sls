{% set current_path = salt['environ.get']('PATH', '/bin:/usr/bin') %}
{% set conda_path = '/home/' + grains['deescalated_user'] + '/miniconda3' %}
{% set conda_bin_path = conda_path + '/bin' %}

install_conda_pip_requirements:
  cmd.run:
    - name: |
        source activate conda_env
        pip install -r {{ grains['project'] }}/{{ grains['pip_req_path'] }}
    - cwd: /home/{{ grains['deescalated_user'] }}
    - runas: {{ grains['deescalated_user'] }}
    - env:
      - PATH: {{ [current_path, conda_bin_path]|join(':') }}
    - require:
      - sls: conda
