setup_apt_mirror:
  pkg.installed:
    - pkgs:
      - apt-mirror
    - require:
      - sls: nginx.general-mirror

/etc/apt/mirror.list:
  file.managed:
    - source: salt://mirrors/apt-mirror.list

/var/www/html/debian:
  file.symlink:
    - target: /var/spool/apt-mirror/mirror/ftp.us.debian.org/debian

/var/www/html/apt:
  file.symlink:
    - target: /var/spool/apt-mirror/mirror/repo.saltstack.com/apt

start_apt_mirror:
  cmd.run:
    - name: nohup apt-mirror
    - cwd: /home/{{ grains['deescalated_user'] }}
    - bg: True
