install_ambari_package:
  pkg.installed:
    - pkgs:
      - ambari-server
    - require:
      - sls: hadoop.hortonworks

setup_ambari_package:
  cmd.run:
    - name: ambari-server setup --silent

start_ambari_server:
  cmd.run:
    - name: ambari-server start
