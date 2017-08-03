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
    # - git
    # - git.ssh
    # - git.repo
    # - artifacts               {# requires {{ grains['dvcs'] }}.repo #}
    # - nginx                   {# requires {{ grains['dvcs'] }}.repo #}
    # - venv                    {# requires {{ grains['dvcs'] }}.repo, python #}
    # - venv.pip_requirements   {# requires venv #}
    # - miniconda               {# requires users #}
    # - miniconda.pip_requirements   {# requires miniconda_env #}
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
