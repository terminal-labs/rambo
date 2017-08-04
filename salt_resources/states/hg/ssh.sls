hg_add_host_fingerprint:
  ssh_known_hosts:
    - present
    - fingerprint: {{ grains['fingerprint'] }}
    - timeout: 90
