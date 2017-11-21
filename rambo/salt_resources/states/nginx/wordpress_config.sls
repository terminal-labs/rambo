ngingx_conf:
  file.managed:
    - name: /etc/nginx/sites-enabled/nginx.conf
    - source: salt:///nginx/wordpress_nginx.conf.template

/etc/nginx/sites-enabled/default:
  file.absent

nginx_restart:
  module.run:
    - name: service.restart
    - m_name: nginx
