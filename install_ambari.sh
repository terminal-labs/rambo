apt-get update
apt-get install wget

wget -nv http://public-repo-1.hortonworks.com/ambari/debian7/2.x/updates/2.2.0.0/ambari.list -O /etc/apt/sources.list.d/ambari.list
apt-key adv --recv-keys --keyserver keyserver.ubuntu.com B9733A7A07513CAD

apt-get update

apt-get install -y ambari-server

ambari-server setup --silent

ambari-server start
