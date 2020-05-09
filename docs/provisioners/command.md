# Command Provisioning

Rambo is able to provision with a command. This command can be passed to `rambo up` in the cli, or set in the `rambo.conf`. For example:

```shell
rambo up -c "hostname"
```

will provision and run the command `hostname`, displaying the hostname of the instance as part of the provisioning process. This can be replaced with any command for something more useful.
