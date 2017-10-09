{% for file in ['libjpeg.so','libfreetype.so','libz.so'] %}
/usr/lib/{{ file }}:
  file.symlink:
    - target: /usr/lib/x86_64-linux-gnu/{{ file }}
{% endfor %}
