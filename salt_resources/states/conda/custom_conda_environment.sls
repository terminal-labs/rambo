{% set saltstates = 'inflation-conductor-server-rambo' %}
install_venv_conda_requirements:
  cmd.run:
    - name: miniconda3/bin/conda env update --name conda_env --file {{ grains['project'] }}/{{ grains['conda_req_path'] }}
    - cwd: /home/{{ grains['deescalated_user'] }}
    - runas: {{ grains['deescalated_user'] }}
    - require:
      - sls: {{ saltstates }}.conda
      - sls: {{ saltstates }}.git.repo
