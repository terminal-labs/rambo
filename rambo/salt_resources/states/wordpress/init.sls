creat_db_for_wordpress:
  cmd.run:
    - name: mysql -u root -e "CREATE DATABASE wordpress"
    - cwd: /home/{{ grains['deescalated_user'] }}
    - runas: {{ grains['deescalated_user'] }}

creat_db_user_wordpress:
  cmd.run:
    - name: mysql -u root -e "CREATE USER wordpressuser@localhost IDENTIFIED BY 'password'"
    - cwd: /home/{{ grains['deescalated_user'] }}
    - runas: {{ grains['deescalated_user'] }}

grant_db_privileges:
  cmd.run:
    - name: mysql -u root -e "GRANT ALL PRIVILEGES ON wordpress.* TO wordpressuser@localhost"
    - cwd: /home/{{ grains['deescalated_user'] }}
    - runas: {{ grains['deescalated_user'] }}

flush_db_privileges:
  cmd.run:
    - name: mysql -u root -e "FLUSH PRIVILEGES"
    - cwd: /home/{{ grains['deescalated_user'] }}
    - runas: {{ grains['deescalated_user'] }}

download_wordpress:
  cmd.run:
    - name: wget http://wordpress.org/latest.tar.gz
    - cwd: /home/{{ grains['deescalated_user'] }}
    - runas: {{ grains['deescalated_user'] }}

unzip_wordpress:
  cmd.run:
    - name: tar xzvf latest.tar.gz
    - cwd: /home/{{ grains['deescalated_user'] }}
    - runas: {{ grains['deescalated_user'] }}

place_wordpress:
  file.managed:
    - name: /home/{{ grains['deescalated_user'] }}/wordpress/wp-config.php
    - source: salt:///wordpress/wp-config.php.template

move_wordpress:
  cmd.run:
    - name: rsync -avP /home/{{ grains['deescalated_user'] }}/wordpress/ /var/www/html/
    - cwd: /home/{{ grains['deescalated_user'] }}
