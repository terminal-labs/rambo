base:
  'roles:project':
    - match: grain
    - clean
    - basebox
    - basebox.symlink
    - users                     {# requires basebox #}
    - python
    # - network
    # - network.cluster
    # - hg
    # - hg.ssh
    # - hg.repo
    # - git
    # - git.ssh
    # - git.repo
    # - database                {# required_in postgres #}
    # - artifacts               {# requires {{ grains['dvcs'] }}.repo, required_in postgres #}
    # - nginx                   {# requires {{ grains['dvcs'] }}.repo #}
    # - venv                    {# requires {{ grains['dvcs'] }}.repo, python #}
    # - venv.pip_requirements   {# requires venv #}
    # - conda                   {# requires users #}
    # - conda.anaconda          {# requires conda #}
    # - conda.anaconda_license  {# requires conda.anaconda #}
    # - conda.pip_requirements  {# requires conda #}
    # - postgresql              {# requires {{ grains['dvcs'] }}.repo #}
    # - conf
    # - django
    # - supervisord
    # - hadoop.ambari
  'roles:prod':
    - match: grain
    - deploy_keys
    - supervisord.start         {# requires supervisor #}
  'roles:dev':
    - match: grain
    - users.aliases             {# requires users #}
