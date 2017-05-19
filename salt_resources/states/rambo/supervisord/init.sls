install_supervisor:
  pkg.installed:
    - pkgs:
      - supervisor

supervisord_config_file:
  file.managed:
    - template: jinja
    - name: /etc/supervisor/conf.d/project.conf
    - source: salt://supervisord/project.conf.template
