# Script Provisioning

Rambo is able to provision with a script. This provisioning step runs after an optional step for a [custom provisioning command](command). The path (on the host) to this script can be passed to `rambo up` in the cli, or set in the `rambo.conf`. For example, given the following file in the Rambo project directory on the host


```python
#!/usr/bin/env python3

import socket

print(socket.gethostname())
```

this will display the hostname, according to Python


```shell
rambo up -s echo_hostname.py
```
