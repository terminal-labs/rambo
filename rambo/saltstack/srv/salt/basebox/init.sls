{% set os, os_family = salt['grains.item']('os', 'os_family') %}

setup_basebox:
  pkg.installed:
    - pkgs:
      - rsync
      - p7zip
      - zip
      - unzip
      - wget
      - curl
      - nano
      - emacs
{% if os_family == 'Debian'%}
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
{% elif os == 'RedHat' %}
      - epel-release
{% endif %}
