install_ambari_agent_package:
  pkg.installed:
    - pkgs:
      - ambari-agent

place_ambari_agent_file:
  file.managed:
    - name: /etc/ambari-agent/conf/ambari-agent.ini
    - source: salt://hadoop-edgenode-rambo/hadoop/ambari-agent.ini
