install_miniconda_pip_requirements:
  cmd.run:
    - name: ./bin/pip install -r /home/{{ grains['deescalated_user'] }}/{{ grains['project'] }}/{{ grains['pip_req_path'] }}
    - runas: {{ grains['deescalated_user'] }}
    - require:
      - sls: miniconda_env
