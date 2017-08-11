system:
  network.system:
    - enabled: True # only neccessary as a bypass for https://github.com/saltstack/salt/issues/6922
    - hostname: {{ grains['hostname'] }}
    - apply_hostname: True
    - retain_settings: True
