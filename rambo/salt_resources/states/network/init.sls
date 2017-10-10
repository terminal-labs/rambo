127.0.1.1:
  host.only:
    - hostnames:
      {% if 'domain' in grains %}
      - {{ grains['hostname'] }}.{{ grains['domain'] }}
      {% endif %}
      - {{ grains['hostname'] }}
