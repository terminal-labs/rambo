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
    - require:
      - sls: {{ grains['dvcs'] }}.repo
    - name: sftp -r ftp@{{ grains['artifact_server_address'] }}:{{ grains['artifact_db_path'] }}/{{ grains['artifact_db'] }}
    - cwd: /home/{{ grains['deescalated_user'] }}/{{ grains['project'] }}

/home/{{ grains['deescalated_user'] }}/{{ grains['project'] }}/{{ grains['artifact_db'] }}:
  file.managed:
    - replace: False
    - user: {{ grains['deescalated_user'] }}
    - group: {{ grains['deescalated_user'] }}
