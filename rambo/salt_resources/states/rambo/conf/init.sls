/home/{{ grains['deescalated_user'] }}/{{ grains['project'] }}/conf/settings.ini:
  file.managed:
    - source: salt://conf/settings.ini
    - makedirs: True
    - user: {{ grains['deescalated_user'] }}
    - group: {{ grains['deescalated_user'] }}
    - template: jinja

/home/{{ grains['deescalated_user'] }}/{{ grains['project'] }}/conf/debug.txt:
  file.managed:
    - user: {{ grains['deescalated_user'] }}
    - group: {{ grains['deescalated_user'] }}

/home/{{ grains['deescalated_user'] }}/{{ grains['project'] }}/conf/running_in_vagrant.txt:
  file.managed:
    - user: {{ grains['deescalated_user'] }}
    - group: {{ grains['deescalated_user'] }}
