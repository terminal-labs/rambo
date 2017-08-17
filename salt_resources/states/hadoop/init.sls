{% if 'cluster_nodes' in grains %}
{% for node in grains['cluster_nodes'] if (node != 'rambo-nix-rambo-lgkzsq') %}
{{ grains['cluster_nodes'][node] }}:
  host.only:
    - hostnames:
      {% if grains['domain'] %}
      - {{ node }}.{{ grains['domain'] }}
      {% endif %}
      - {{ node }}
{% endfor %}
{% endif %}
