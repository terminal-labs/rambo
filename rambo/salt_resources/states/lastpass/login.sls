lastpass_login:
  cmd.run:
    - name: export LPASS_DISABLE_PINENTRY=1; cat /vagrant/lpass_password.txt | lpass login --trust api@terminallabs.com
    - cwd: /home/{{ grains['deescalated_user'] }}
    - require:
      - sls: lastpass
