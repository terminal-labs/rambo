system:
  network.system:
    - enabled: True # workaround for https://github.com/saltstack/salt/issues/6922
    - hostname: {{ grains['hostname'] }}
    - apply_hostname: True
    - retain_settings: True
    - required_in: # workaround for https://github.com/saltstack/salt/issues/42926
        cmd: 127.0.1.1

127.0.1.1:
  host.only:
    - hostnames:
      {% if 'domain' in grains %}
      - {{ grains['hostname'] }}.{{ grains['domain'] }}
      {% endif %}
      - {{ grains['hostname'] }}
