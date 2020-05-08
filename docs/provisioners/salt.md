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

If you wish to sepeartely track this code, you could add these two host directories into your Rambo projects `.gitignore` and simply have checkouts of these repositories, or add them as submodules.

#### Legacy Salt directory

Prior to Rambo v0.5, a different directory structure was used for provisioning and this provisioning occured by default. Now, all but the most basic provisioning is opt-in. This form is still supported for now and can be used with `--provision-with-salt-legacy`.
