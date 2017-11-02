{% set os = salt['grains.get']('os') %}

setup_basebox:
  pkg.installed:
    - pkgs:
      - build-essential
      - libreadline6-dev
      - libbz2-dev
      - libssl-dev
      - libsqlite3-dev
      - libncursesw5-dev
      - libffi-dev
      - libdb-dev
      - libexpat1-dev
      - zlib1g-dev
      - liblzma-dev
      - libgdbm-dev
      - libffi-dev
      - libmpdec-dev
      - libfreetype6-dev
      - libpq-dev
      - rsync
      - p7zip
      - zip
      - unzip
      - wget
      - curl
      - nano
      - emacs

{% if os == 'Ubuntu' %}
setup_ubuntu_basebox_deps:
  pkg.installed:
    - pkgs:
      - libjpeg-turbo8-dev
{% endif %}

{% if os == 'Debian' %}
setup_debian_basebox_deps:
  pkg.installed:
    - pkgs:
      - libjpeg62-turbo-dev
{% endif %}

ensure_bashrc_exists:
  file.exists:
    - name: /home/{{ grains['deescalated_user'] }}/.bashrc
