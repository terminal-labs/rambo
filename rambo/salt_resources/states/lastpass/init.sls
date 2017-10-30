install_lastpass_debs:
  pkg.installed:
    - pkgs:
      - openssl
      - libcurl3
      - libxml2
      - libssl-dev
      - libxml2-dev
      - libcurl4-openssl-dev
      - pinentry-curses
      - cmake
      - pkg-config
      - xclip

clone_lastpass_rep:
   git.latest:
     - name: https://github.com/lastpass/lastpass-cli.git
     - target: /home/{{ grains['deescalated_user'] }}/lastpass-cli
     - runas: {{ grains['deescalated_user'] }}
     - require:
       - sls: git.ssh

lastpass_cmake:
  cmd.run:
    - name: cmake .
    - cwd: /home/{{ grains['deescalated_user'] }}/lastpass-cli
    - runas: {{ grains['deescalated_user'] }}

lastpass_make:
  cmd.run:
    - name: make
    - cwd: /home/{{ grains['deescalated_user'] }}/lastpass-cli
    - runas: {{ grains['deescalated_user'] }}

create_lastpass_dir:
  file.directory:
    - name: /home/{{ grains['deescalated_user'] }}/.config/lastpass
    - user: {{ grains['deescalated_user'] }}
    - group: {{ grains['deescalated_user'] }}
    - makedirs: True

create_primary_lastpass_dir:
  file.directory:
    - name: /home/{{ grains['deescalated_user'] }}/.config/lastpass
    - user: {{ grains['deescalated_user'] }}
    - group: {{ grains['deescalated_user'] }}
    - makedirs: True

create_secondary_lastpass_dir:
  file.directory:
    - name: /home/{{ grains['deescalated_user'] }}/.local/share/lpass
    - user: {{ grains['deescalated_user'] }}
    - group: {{ grains['deescalated_user'] }}
    - makedirs: True

create_tertiary_lastpass_dir:
  file.directory:
    - name: /run/user/1000/lpass
    - makedirs: True

lastpass_install:
  cmd.run:
    - name: make install
    - cwd: /home/{{ grains['deescalated_user'] }}/lastpass-cli

clean_lastpass_build_dir:
  file.directory:
    - name: /home/{{ grains['deescalated_user'] }}/lastpass-cli
    - clean: True

remove_lastpass_build_dir:
  cmd.run:
    - name: rm -rf lastpass-cli
    - cwd: /home/{{ grains['deescalated_user'] }}
