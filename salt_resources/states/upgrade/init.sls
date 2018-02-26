update_aptget_db:
  module.run:
    - name: pkg.refresh_db

upgrade_all_aptget_packages:
  module.run:
    - name: pkg.upgrade

update_apt_db:
  cmd.run:
    - name: apt update --yes --quiet

upgrade_all_apt_packages:
  cmd.run:
    - name: apt upgrade --yes --quiet

upgrade_all_certs:
  cmd.run:
    - name: apt install ca-certificates --yes --quiet
