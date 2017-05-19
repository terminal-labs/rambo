nginx_install: 
  pkg.installed:
    - name: nginx-full
  service.running:
    - name: nginx
    - enable: True

nging_conf:
  file.managed:
    - name: /home/{{ grains['deescalated_user'] }}/{{ grains['project'] }}/nginx.conf
    - require:
      - sls: {{ grains['dvcs'] }}.repo
    - template: jinja
    - source: /home/{{ grains['deescalated_user'] }}/{{ grains['project'] }}/nginx.conf.template
    - user: {{ grains['deescalated_user'] }}
    - group: {{ grains['deescalated_user'] }}

nginx_symlink:
  file.symlink:
    - name: /etc/nginx/sites-enabled/nginx.conf
    - target: /home/{{ grains['deescalated_user'] }}/{{ grains['project'] }}/nginx.conf

/etc/nginx/sites-enabled/default:
  file.absent

nginx_restart:
  module.run:
    - name: service.restart
    - m_name: nginx
