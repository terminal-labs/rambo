{% set current_path = salt['environ.get']('PATH', '/bin:/usr/bin') %}
{% set conda_path = '/home/' + grains['deescalated_user'] + '/miniconda3' %}
{% set conda_bin_path = conda_path + '/bin' %}

place_before_license_application_file:
  file.managed:
    - name: /home/{{ grains['deescalated_user'] }}/before_license_application.yml
    - source: salt://conda/before_license_application.yml
    - user: {{ grains['deescalated_user'] }}
    - group: {{ grains['deescalated_user'] }}
    - require:
      - sls: conda.anaconda

before_conda_license:
  cmd.run:
    - name: miniconda3/bin/conda env update --name root --file before_license_application.yml
    - cwd: /home/{{ grains['deescalated_user'] }}
    - runas: {{ grains['deescalated_user'] }}

create_continuum_dir:
  file.directory:
    - name:  /home/{{ grains['deescalated_user'] }}/.continuum
    - user:  {{ grains['deescalated_user'] }}
    - group: {{ grains['deescalated_user'] }}

place_license_file:
  file.managed:
    - name: /home/{{ grains['deescalated_user'] }}/.continuum/{{ grains['anaconda_license'] }}
    - source: salt://files/licenses/anaconda/{{ grains['anaconda_license'] }}
    - user: {{ grains['deescalated_user'] }}
    - group: {{ grains['deescalated_user'] }}

place_after_license_application_file:
  file.managed:
    - name: /home/{{ grains['deescalated_user'] }}/after_license_application.yml
    - source: salt://conda/after_license_application.yml
    - user: {{ grains['deescalated_user'] }}
    - group: {{ grains['deescalated_user'] }}

after_conda_license:
  cmd.run:
    - name: miniconda3/bin/conda env update --name root --file after_license_application.yml
    - cwd: /home/{{ grains['deescalated_user'] }}
    - runas: {{ grains['deescalated_user'] }}
