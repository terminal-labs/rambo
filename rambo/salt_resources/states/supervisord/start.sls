start_service:
  cmd.run:
    - name: "supervisorctl reread; supervisorctl update"
    - require:
      - sls: supervisord
