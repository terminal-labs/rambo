{% set current_path = salt['environ.get']('PATH', '/bin:/usr/bin') %}
{% set conda_path = '/home/' + grains['deescalated_user'] + '/miniconda3' %}
{% set conda_bin_path = conda_path + '/bin' %}

install_jupyter:
  cmd.run:
    - name: conda install -n conda_env -y jupyter -c anaconda
    - runas: {{ grains['deescalated_user'] }}
    - env:
      - PATH: {{ [current_path, conda_bin_path]|join(':') }}
    - require:
      - sls: conda
      - sls: conda.anaconda

create_jupyter_root_dir:
  file.directory:
    - name: /home/{{ grains['deescalated_user'] }}/.jupyter
    - user: {{ grains['deescalated_user'] }}
    - group: {{ grains['deescalated_user'] }}

create_jupyter_runtime_dir:
  file.directory:
    - name: /var/tmp/jupyter_runtime
    - user: {{ grains['deescalated_user'] }}
    - group: {{ grains['deescalated_user'] }}

place_jupyter_notebook_config_py_file:
  file.managed:
    - name: /home/{{ grains['deescalated_user'] }}/.jupyter/jupyter_notebook_config.py
    - source: salt://conda/jupyter_notebook_config.py
    - user: {{ grains['deescalated_user'] }}
    - group: {{ grains['deescalated_user'] }}

place_jupyter_notebook_config_json_file:
  file.managed:
    - name: /home/{{ grains['deescalated_user'] }}/.jupyter/jupyter_notebook_config.json
    - source: salt://conda/jupyter_notebook_config.json
    - user: {{ grains['deescalated_user'] }}
    - group: {{ grains['deescalated_user'] }}

load_runtime_env_vars_for_jupyter:
   environ.setenv:
     - name: JUPYTER_RUNTIME_DIR
     - value: /var/tmp/jupyter_runtime
     - update_minion: True

start_jupyter:
  cmd.run:
    - name: |
        source activate conda_env
        nohup /home/{{ grains['deescalated_user'] }}/miniconda3/envs/conda_env/bin/jupyter notebook --ip='*' --port 8080 &
    - cwd: /home/{{ grains['deescalated_user'] }}
    - runas: {{ grains['deescalated_user'] }}
    - bg: True
    - env:
      - PATH: {{ [current_path, conda_bin_path]|join(':') }}
