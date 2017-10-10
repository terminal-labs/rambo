/etc/apt/sources.list.d/pgdg.list:
  file.managed:
    - source: salt://postgresql/pgdg.list

postgresql_ppa_keys:
  cmd.run:
    - name: "wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -"
    - cwd: /home/{{ grains['deescalated_user'] }}

install_postgresql:
  pkg.installed:
    - refresh: True
    - pkgs:
      - postgresql-9.4

postgres_conf:
  file.managed:
    - template: jinja
    - name: /etc/postgresql/9.4/main/pg_hba.conf
    - source: salt://postgresql/pg_hba.conf.template

restart_postgresql:
  module.run:
    - name: service.restart
    - m_name: postgresql

djangouser:
  postgres_user.present:
    - name: django
    - password: {{ grains['postgres_password'] }}
    - user: postgres

djangodb:
  postgres_database.present:
    - name: {{ grains['project'] }}
    - encoding: UTF8
    - lc_ctype: en_US.UTF8
    - lc_collate: en_US.UTF8
    - template: template0
    - owner: django
    - user: postgres

enable_postgresql_rstart_on_reboot:
  cmd.run:
    - name: "/usr/sbin/update-rc.d postgresql enable"

load_db:
  cmd.run:
    - require:
      - sls: {{ grains['dvcs'] }}.repo
    - name: |
        echo "*:*:{{ grains['project'] }}:django:{{ grains['postgres_password'] }}" > $HOME/.pgpass
        chmod 0600 $HOME/.pgpass
        psql -U django {{ grains['project'] }} < {{ grains['db_dump'] }}
    - cwd: /home/{{ grains['deescalated_user'] }}/{{ grains['project'] }}/
    - runas: {{ grains['deescalated_user'] }}
