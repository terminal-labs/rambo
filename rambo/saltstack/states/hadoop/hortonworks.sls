{% if grains['os'] == 'Ubuntu' and grains['osmajorrelease'] == 14 %}
add_ambari_ppa_keys:
  cmd.run:
    - name: wget -nv http://public-repo-1.hortonworks.com/ambari/debian7/2.x/updates/2.2.0.0/ambari.list -O /etc/apt/sources.list.d/ambari.list | apt-key adv --recv-keys --keyserver keyserver.ubuntu.com B9733A7A07513CAD
    - cwd: /home/{{ grains['deescalated_user'] }}

update_apt_post_ambari_ppa_keys_addition:
  module.run:
    - name: pkg.refresh_db
{% endif %}
