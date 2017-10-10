{% set saltstates = 'inflation-conductor-server-rambo' %}
place_conda_environment_file:
  file.managed:
    - name: /home/{{ grains['deescalated_user'] }}/default_conda_environment.yml
    - source: salt://{{ saltstates }}/conda/default_conda_environment.yml
    - require:
      - sls: {{ saltstates }}.conda

install_deps_from_conda_environment_file:
  cmd.run:
    - name: miniconda3/bin/conda env update --name conda_env --file default_conda_environment.yml
    - cwd: /home/{{ grains['deescalated_user'] }}
    - runas: {{ grains['deescalated_user'] }}
