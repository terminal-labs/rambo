create_digitalocean_auth_dir:
  file.directory:
    - name: /home/{{ grains['deescalated_user'] }}/auth/digitalocean
    - user: {{ grains['deescalated_user'] }}
    - group: {{ grains['deescalated_user'] }}
    - makedirs: True

get_do_token_lastpass:
  cmd.run:
    - name: export LPASS_DISABLE_PINENTRY=1; cat /vagrant/lpass_password.txt | lpass show do-token --notes >> auth/digitalocean/do-token
    - cwd: /home/{{ grains['deescalated_user'] }}
    - require:
      - sls: lastpass.login
