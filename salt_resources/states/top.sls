base:
  'roles:project':
    - match: grain
    - clean
    - basebox
    - basebox.symlink
    - basebox.miniconda
    - users
    - python
    # - hg
    # - hg.ssh
    # - hg.repo
    # - artifacts               {# requires {{ grains['dvcs'] }}.repo #}
    # - nginx                   {# requires {{ grains['dvcs'] }}.repo #}
    # - venv                    {# requires {{ grains['dvcs'] }}.repo, python #}
    # - venv.pip_requirements   {# requires venv #}
    - miniconda_env           {# requires {{ grains['dvcs'] }}.repo, python #}
    # - miniconda_env.pip_requirements   {# requires miniconda_env #}
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
