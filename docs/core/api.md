# Python API

Rambo's CLI and Python API are compatible. In other words, what you can do in the CLI, you can do in the Python API. To accomplish this the CLI is largely dependant on the Python API. You can access the Python API by importing the various functions in app.py, such as with `from rambo.app import up`

Through the Python API you can call `up` and `destroy` to create and destroy VMs. `ssh` is also available and presents an interactive shell to the VM, as if you ran `rambo ssh` with the CLI.

CLI options are available to be set as either functions in app.py, or as parameters to those functions, depending on whether the CLI option was on `rambo` or a command (e.g. `up`). For instance, the following are equivalent:

```shell
rambo --vagrant-cwd /sample/path up -p virtualbox
```

```python
from rambo.app import up
up(vagrant_cwd,"/sample/path", provider="virtualbox")
```
