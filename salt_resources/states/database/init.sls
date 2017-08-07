set_db_from local:
  file.managed:
    {% if salt['file.file_exists' ]('/database/' + grains['db_name']) %}
    - source: salt://database/{{ grains['db_name'] }}
    {% else %} # Create empty db
    - contents: ""
    {% endif %}
    - name: /home/{{ grains['deescalated_user'] }}/{{ grains['project'] }}/{{ grains['db_dump'] }}
    - replace: False
    - user: {{ grains['deescalated_user'] }}
    - group: {{ grains['deescalated_user'] }}
    - require_in:
        cmd: load_db
