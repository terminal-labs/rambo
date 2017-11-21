vpn_install:
  pkg.installed:
    - pkgs:
      - openvpn
      - easy-rsa

vpn_config:
  cmd.run:
    - name: make-cadir ~/openvpn-ca
    - cwd: /home/{{ grains['deescalated_user'] }}
    - runas: {{ grains['deescalated_user'] }}


vpn_conf:
  file.managed:
    - name: /home/{{ grains['deescalated_user'] }}/openvpn-ca/vars
   - template: jinja
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

# vpn_build-HMAC:
#   cmd.run:
#     - name: source vars; openvpn --genkey --secret keys/ta.key
#     - cwd: /home/{{ grains['deescalated_user'] }}/openvpn-ca
#     - runas: {{ grains['deescalated_user'] }}


# vpn_restart:
#   module.run:
#     - name: service.restart
#     - m_name: openvpn
