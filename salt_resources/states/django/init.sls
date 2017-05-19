django_collectstatic:
  cmd.run:
    - name: ../venv/bin/python manage.py collectstatic --noinput 
    - cwd: /home/{{ grains['deescalated_user'] }}/{{ grains['project'] }}/
    - runas: {{ grains['deescalated_user'] }}
