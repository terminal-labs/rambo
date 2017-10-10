install_venv_pip_requirements:
  cmd.run:
    - name: ./venv/bin/pip install -r {{ grains['project'] }}/{{ grains['pip_req_path'] }}
    - cwd: /home/{{ grains['deescalated_user'] }}
    - runas: {{ grains['deescalated_user'] }}
    - require:
      - sls: venv
