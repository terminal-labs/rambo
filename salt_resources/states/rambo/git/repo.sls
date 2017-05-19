clone_app:
   git.latest:
     - name: {{ grains['repository'] }}
     - target: /home/{{ grains['deescalated_user'] }}/{{ grains['project'] }}
     - user: root

repo_permissions:
  file.directory:
    - name: /home/{{ grains['deescalated_user'] }}/{{ grains['project'] }}
    - user: {{ grains['deescalated_user'] }}
    - group: {{ grains['deescalated_user'] }}
    - recurse:
      - user
      - group
