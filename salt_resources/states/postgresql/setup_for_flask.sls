pg_db_user:
  postgres_user.present:
    - name: flask
    - password: {{ grains['postgres_password'] }}
    - user: postgres

pg_db:
  postgres_database.present:
    - name: {{ grains['project'] }}
    - encoding: UTF8
    - lc_ctype: en_US.UTF8
    - lc_collate: en_US.UTF8
    - template: template0
    - owner: flask
    - user: postgres
