delete_{{ grains['project'] }}:
  file.absent:
    - name: /home/{{ grains['deescalated_user'] }}/{{ grains['project'] }}

delete_localpython:
  file.absent:
    - name: /home/{{ grains['deescalated_user'] }}/.localpython

delete_python_src:
  file.absent:
    - name: /home/{{ grains['deescalated_user'] }}/.python2.7_src