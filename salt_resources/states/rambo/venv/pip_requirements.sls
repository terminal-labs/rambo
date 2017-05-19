install_pip_requirements:
  cmd.run:
    - require:
      - sls: venv
    - name: ./bin/pip install -r /home/{{ grains['deescalated_user'] }}/{{ grains['project'] }}/{{ grains['pip_req_path'] }}
    - cwd: /home/{{ grains['deescalated_user'] }}/venv/
    - runas: {{ grains['deescalated_user'] }}
