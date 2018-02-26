install_php:
  pkg.installed:
    - pkgs:
      - php5
      - php5-fpm
      - php5-mysql
      - php5-gd
      - libssh2-php

/etc/php5/fpm/php.ini:
  file.managed:
    - source: salt://php/php.ini.template
    - user: {{ grains['deescalated_user'] }}
    - group: {{ grains['deescalated_user'] }}

sudo_service_php5fpm_restart:
  cmd.run:
    - name: sudo service php5-fpm restart

php_index_file:
  file.managed:
    - name: /var/www/html/index.php
    - source: salt:///php/index.php.template

php_info_file:
  file.managed:
    - name: /var/www/html/info.php
    - source: salt:///php/info.php.template
