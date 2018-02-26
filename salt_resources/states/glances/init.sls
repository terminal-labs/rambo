install_glances_deps:
  cmd.run:
    - name: pip install bottle
    - cwd: /home/{{ grains['deescalated_user'] }}
    - runas: {{ grains['deescalated_user'] }}

install_glances:
  pkg.installed:
    - pkgs:
      - glances

start_glances:
  cmd.run:
    - name: nohup glances -w -p 8888
    - cwd: /home/{{ grains['deescalated_user'] }}
    - runas: {{ grains['deescalated_user'] }}
    - bg: True
