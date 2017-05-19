base:
  'roles:project':
    - match: grain
    - clean
    - basebox
    - basebox.symlink
    - users
    - python
    # - hg
    # - hg.ssh
    # - hg.repo
    # - artifacts               {# requires {{ grains['dvcs'] }}.repo #}
    # - nginx                   {# requires {{ grains['dvcs'] }}.repo #}
    # - venv                    {# requires {{ grains['dvcs'] }}.repo, python #}
    # - venv.pip_requirements   {# requires venv #}
    # - postgresql              {# requires {{ grains['dvcs'] }}.repo #}
    # - conf
    # - django
    # - supervisord
  'roles:prod':
    - match: grain
    - deploy_keys
    - supervisord.start         {# requires supervisor #}
  'roles:dev':
    - match: grain
    - users.aliases             {# requires users #}
