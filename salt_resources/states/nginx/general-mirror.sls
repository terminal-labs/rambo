test_nginx:
  cmd.run:
    - name: /etc/init.d/nginx configtest
    - cwd: /home/{{ grains['deescalated_user'] }}
    - require:
      - sls: nginx

/var/www/html/index.nginx-debian.html:
  file.absent

/etc/nginx/sites-enabled/default:
  file.absent

/etc/nginx/sites-enabled/nginx.conf:
  file.managed:
    - source: salt://nginx/general-mirror-nginx.conf

restart_nginx:
  module.run:
    - name: service.restart
    - m_name: nginx
