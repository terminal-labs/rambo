{% set saltstates = 'rambo' %}
include:
    - {{ saltstates }}.clean
    - {{ saltstates }}.basebox
    - {{ saltstates }}.basebox.symlink
    - {{ saltstates }}.users                     {# requires basebox #}
    - {{ saltstates }}.python
    # - {{ saltstates }}.network
    # - {{ saltstates }}.network.cluster
    # - {{ saltstates }}.hg
    # - {{ saltstates }}.hg.ssh
    # - {{ saltstates }}.hg.repo
    # - {{ saltstates }}.git
    # - {{ saltstates }}.git.ssh
    # - {{ saltstates }}.git.repo
    # - {{ saltstates }}.database                {# required_in postgres #}
    # - {{ saltstates }}.artifacts               {# requires {{ grains['dvcs'] }}.repo, required_in postgres #}
    # - {{ saltstates }}.nginx                   {# requires {{ grains['dvcs'] }}.repo #}
    # - {{ saltstates }}.venv                    {# requires {{ grains['dvcs'] }}.repo, python #}
    # - {{ saltstates }}.venv.pip_requirements   {# requires venv #}
    # - {{ saltstates }}.conda                   {# requires users #}
    # - {{ saltstates }}.conda.anaconda          {# requires conda #}
    # - {{ saltstates }}.conda.anaconda_license  {# requires conda.anaconda #}
    # - {{ saltstates }}.conda.pip_requirements  {# requires conda #}
    # - {{ saltstates }}.postgresql              {# requires {{ grains['dvcs'] }}.repo #}
    # - {{ saltstates }}.conf
    # - {{ saltstates }}.django
    # - {{ saltstates }}.supervisord
    # - {{ saltstates }}.hadoop.ambari
