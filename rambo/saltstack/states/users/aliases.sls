add_alias_emacsclient:
  cmd.run:
    - name: echo "alias emacs='emacsclient -a \"\" -t'" >> .bash_aliases
    - cwd: /home/{{ grains['deescalated_user'] }}
    - runas: {{ grains['deescalated_user'] }}
    - require:
      - sls: users