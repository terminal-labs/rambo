{% set os, os_family = salt['grains.item']('os', 'os_family') %}

{% if os == 'CentOS' %}
install_ius_for_centos:
  cmd.run:
    - name: yum -y install https://centos7.iuscommunity.org/ius-release.rpm
{% endif %}

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
{% endif %}
{% if os == 'Ubuntu' %}
      - libjpeg-turbo8-dev
{% endif %}
{% if os == 'Debian' %}
      - libjpeg62-turbo-dev
{% endif %}
{% if os == 'CentOS' %}
      - epel-release
{% endif %}

{% if os == 'CentOS' %}
special_group_install_for_centos:
  cmd.run:
    - name: yum -y groupinstall 'Development Tools'

special_post_install_yum_update_for_centos:
  cmd.run:
    - name: yum -y update
{% endif %}

ensure_bashrc_exists:
  file.exists:
    - name: /home/{{ grains['deescalated_user'] }}/.bashrc
