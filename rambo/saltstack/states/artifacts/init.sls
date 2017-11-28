artifact_server:
  ssh_known_hosts:
    - present
    - enc: ecdsa
    - user: root
    - fingerprint: {{ grains['artifact_server_fingerprint'] }}
    - name: {{ grains['artifact_server_address'] }}
    - timeout: 30

download_media:
  cmd.run:
    - require:
      - sls: {{ grains['dvcs'] }}.repo
    - name: sftp -r ftp@{{ grains['artifact_server_address'] }}:{{ grains['artifact_files'] }}
    - cwd: /home/{{ grains['deescalated_user'] }}/{{ grains['project'] }}/{{ grains['artifact_drop_path'] }}

download_db_dump:
  cmd.run:
    - name: sftp -r ftp@{{ grains['artifact_server_address'] }}:{{ grains['artifact_db_path'] }}/{{ grains['db_dump'] }}
    - cwd: /home/{{ grains['deescalated_user'] }}/{{ grains['project'] }}
    - require:
      - sls: {{ grains['dvcs'] }}.repo
    - require_in:
        cmd: load_db

/home/{{ grains['deescalated_user'] }}/{{ grains['project'] }}/{{ grains['db_dump'] }}:
  file.managed:
    - replace: False
    - user: {{ grains['deescalated_user'] }}
    - group: {{ grains['deescalated_user'] }}
    - require:
        cmd: download_db_dump
