set_db_from local:
  file.managed:
    {% if salt['file.file_exists' ]('/database/dump' + grains['db_dump']) %}
    - source: salt://database/dump/{{ grains['db_dump'] }}
    {% else %} # Create empty db
    - contents: ""
    {% endif %}
    - name: /home/{{ grains['deescalated_user'] }}/{{ grains['project'] }}/{{ grains['db_dump'] }}
    - replace: False
    - user: {{ grains['deescalated_user'] }}
    - group: {{ grains['deescalated_user'] }}
    - require_in:
        cmd: load_db
