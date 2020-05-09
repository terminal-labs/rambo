# Salt

Rambo can provision with Salt. This provisioning occurs after optional provisioning with a [command](command) or [script](script).

By default, a new Rambo project is given some basic, sample salt code in `saltstack/` that would be used for Salt provisioning. To provision with Salt and use this directory, run

```bash
rambo up --provision-with-salt
```

### Salt directory

The `saltstack` directory mimics a typical structure of the Salt code on a Salt Master. Often, a Salt Master's code is tracked in two reporisotries.


Host directory | Target directory
---------------|-----------------
saltstack/etc  | /etc/salt
saltstack/srv  | /srv

With this directory structure, the files are copied over into the instance with no changes, and the instance bootstraps salt with a Master and Minion, and then runs the highstate. What the code is that the Master and Minion do is dependent on just these two directories.

If you wish to sepeartely track this code, you could add these two host directories into your Rambo projects `.gitignore` and simply have checkouts of these repositories, or add them as submodules.

### Bootstrap

If additional Salt aplications are required (like Salt Syndic or Salt Cloud), or specific versions of Salt are needed, this can be specified by passing the bootstrap arguments. For example, this will pass the string `-x python3` as an argument to [salt-bootstrap](https://github.com/saltstack/salt-bootstrap), telling it to install Salt with Python 3.

```bash
rambo up --provision-with-salt --salt-bootstrap-args '-x python3'
```

### Legacy Salt directory

Prior to Rambo version 0.5, a different directory structure was used for provisioning, and this provisioning occured by default. Now, all but the most basic provisioning is opt-in. This form is still supported for now and can be used with `--provision-with-salt-legacy`. This command is mutually exclusive with `--provision-with-salt`. If both are used, `--provision-with-salt` will be preferred.  The legacy provisioning is deprecated because it makes assumptions about the instance that are Rambo specific. This makes it difficult to port a non-Rambo project that uses Salt into Rambo, and export a Rambo project out.
