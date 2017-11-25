{{ grains['deescalated_user'] }}:
  user.present:
    - home: /home/{{ grains['deescalated_user'] }}
    - fullname: {{ grains['deescalated_user'] }}
    - shell: /bin/bash

color_prompt:
  cmd.run:
    - name: sed -i 's/^#force_color_prompt/force_color_prompt/g' .bashrc; sed -i 's/^\s*#alias grep/    alias grep/g' .bashrc
    - cwd: /home/{{ grains['deescalated_user'] }}
    - runas: {{ grains['deescalated_user'] }}
    - require:
      - sls: basebox
