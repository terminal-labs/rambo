sudo mv /etc/salt/minion{,-dist}
sudo cp /vagrant/salt_resources/minions/minion.virtualbox /etc/salt/minion
sudo cp /vagrant/salt_resources/grains/grains /etc/salt/grains
