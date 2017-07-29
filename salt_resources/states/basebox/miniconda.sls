{% set current_path = salt['environ.get']('PATH', '/bin:/usr/bin') %}
{% set miniconda_path = '/usr/local/bin/miniconda/bin' %}

download_miniconda_installer:
  cmd.run:
    - name: wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /home/vagrant/miniconda.sh
    - unless: test -f {{ miniconda_path }}/conda

ensure_miniconda_is_installed:
  cmd.run:
    - name: bash /home/vagrant/miniconda.sh -b -p /usr/local/bin/miniconda
    - unless: test -f {{ miniconda_path }}/conda

{% if not salt['file.search']('/home/vagrant/.bashrc', 'export PATH={{ miniconda_path }}:$PATH') %}
add_conda_to_bashrc:
  file.append:
      - name: /home/vagrant/.bashrc
      - text: export PATH={{ miniconda_path }}:$PATH
      - runas: vagrant
{% endif %}
