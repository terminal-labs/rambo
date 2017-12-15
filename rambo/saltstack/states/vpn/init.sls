vpn_install:
  pkg.installed:
    - pkgs:
      - openvpn
      - easy-rsa

vpn_vars_config:
  cmd.run:
    - name: make-cadir ~/openvpn-ca
    - cwd: /home/{{ grains['deescalated_user'] }}
    - runas: {{ grains['deescalated_user'] }}

vpn_conf:
  file.managed:
    - name: /home/{{ grains['deescalated_user'] }}/openvpn-ca/vars
    - source: salt://vpn/vars
    - user: {{ grains['deescalated_user'] }}
    - group: {{ grains['deescalated_user'] }}

vpn_clean-ca:
  cmd.run:
    - name: source vars; ./clean-all
    - cwd: /home/{{ grains['deescalated_user'] }}/openvpn-ca
    - runas: {{ grains['deescalated_user'] }}

vpn_build-ca:
  cmd.run:
    - name: source vars; ./pkitool --batch --initca
    - cwd: /home/{{ grains['deescalated_user'] }}/openvpn-ca
    - runas: {{ grains['deescalated_user'] }}

vpn_build-key-server:
  cmd.run:
    - name: source vars; ./pkitool --batch --server server
    - cwd: /home/{{ grains['deescalated_user'] }}/openvpn-ca
    - runas: {{ grains['deescalated_user'] }}

vpn_build-Diffie-Hellman:
  cmd.run:
    - name: source vars; ./build-dh
    - cwd: /home/{{ grains['deescalated_user'] }}/openvpn-ca
    - runas: {{ grains['deescalated_user'] }}

vpn_build-HMAC:
  cmd.run:
    - name: source vars; /usr/sbin/openvpn --genkey --secret keys/ta.key
    - cwd: /home/{{ grains['deescalated_user'] }}/openvpn-ca
    - runas: {{ grains['deescalated_user'] }}

vpn_copy-keys:
  cmd.run:
    - name: cp * /etc/openvpn
    - cwd: /home/{{ grains['deescalated_user'] }}/openvpn-ca/keys

vpn_server_conf:
  file.managed:
    - name: /etc/openvpn/server.conf
    - source: salt://vpn/server.conf
    - user: {{ grains['deescalated_user'] }}
    - group: {{ grains['deescalated_user'] }}

vpn_kernel_packet_forwarding:
  cmd.run:
    - name: sed -i 's/^#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/g' /etc/sysctl.conf

vpn_ufw_packet_forward:
  cmd.run:
    - name: sed -i 's/^DEFAULT_FORWARD_POLICY=\"DROP\"/DEFAULT_FORWARD_POLICY=\"ACCEPT\"/g' /etc/default/ufw
    
vpn_ufw_rules:
  file.managed:
    - name: /etc/ufw/before.rules
    - source: salt://vpn/before.rules
    - template: jinja

vpn_ufw_allow_port:
  cmd.run:
    - name: ufw allow 1194/upd; ufw allow OpenSSH

vpn_ufw_restart:
  cmd.run:
    - name: ufw disable; yes | ufw enable

vpn_restart_openvpn_service:
  module.run:
    - name: service.restart
    - m_name: openvpn@server

vpn_create_client_dir:
  file.directory:
    - user: {{ grains['deescalated_user'] }}
    - group: {{ grains['deescalated_user'] }}
    - mode: 700
    - makedirs: True
    - name: /home/{{ grains['deescalated_user'] }}/client-configs/files

vpn_create_client_base:
  file.managed:
    - name: /home/{{ grains['deescalated_user'] }}/client-configs/base.conf
    - source: salt://vpn/base.conf
    - user: {{ grains['deescalated_user'] }}
    - group: {{ grains['deescalated_user'] }}
    - mode: 700

vpn_create_make_config_script:
  file.managed:
    - name: /home/{{ grains['deescalated_user'] }}/client-configs/make_config.sh
    - source: salt://vpn/make_config.sh
    - user: {{ grains['deescalated_user'] }}
    - group: {{ grains['deescalated_user'] }}
    - mode: 700

