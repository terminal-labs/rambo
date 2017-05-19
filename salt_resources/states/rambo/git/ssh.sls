bitbucket.org:
  ssh_known_hosts:
    - present
    - fingerprint: {{ grains['fingerprint'] }}
