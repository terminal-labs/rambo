/root/.ssh/master_bitbucket_deployment_key:
  file.managed:
    - source:
      - salt://ssh_keys/master_bitbucket_deployment_key
    - mode: 400

/root/.ssh/master_artifacts_server_deployment_key:
  file.managed:
    - source:
      - salt://ssh_keys/master_artifacts_server_deployment_key
    - mode: 400

/root/.ssh/config:
  file.managed:
    - source:
      - salt://deploy_keys/config
    - mode: 400