hg_add_host_fingerprint:
  ssh_known_hosts:
    - name: {{ grains['repo_host'] }}
    - present
    - fingerprint: {{ grains['fingerprint'] }}
    - fingerprint_hash_type: md5
    - timeout: 90
