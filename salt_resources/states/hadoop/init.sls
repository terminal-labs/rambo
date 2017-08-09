update_apt_before_hadoop_instalation:
  module.run:
    - name: pkg.refresh_db

refresh_wget:
  pkg.installed:
    - refresh: True
    - pkgs:
      - wget
