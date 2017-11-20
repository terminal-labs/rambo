{% set saltstates = 'rambo' %}
base:
  'roles:project':
    - match: grain
    - {{ saltstates }}
  'roles:prod':
    - match: grain
    - {{ saltstates }}.supervisord.start         {# requires supervisor #}
  'roles:dev':
    - match: grain
    - {{ saltstates }}.users.aliases             {# requires users #}
