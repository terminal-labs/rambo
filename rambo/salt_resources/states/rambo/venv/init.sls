## Commented sections use a compiled python. See srv/salt/python/init.sls
#venv_install:
#  cmd.run:
#    - require:
#      - sls: {{ grains['dvcs'] }}.repo
#      - sls: python
#    - name: virtualenv /home/{{ grains['deescalated_user'] }}/venv --python=/home/{{ grains['deescalated_user'] }}/.localpython/bin/python2.7
#    - runas: {{ grains['deescalated_user'] }}
    
venv_install:
  cmd.run:
    - require:
      - sls: {{ grains['dvcs'] }}.repo
      - sls: python
#    - name: virtualenv /home/{{ grains['deescalated_user'] }}/venv --python=/home/{{ grains['deescalated_user'] }}/.localpython/bin/python2.7
    - name: virtualenv /home/{{ grains['deescalated_user'] }}/venv
    - runas: {{ grains['deescalated_user'] }}

pip_update:
  cmd.run:
    - name: ./bin/pip install -U setuptools; ./bin/pip install -U pip
    - cwd: /home/{{ grains['deescalated_user'] }}/venv/
    - runas: {{ grains['deescalated_user'] }}
