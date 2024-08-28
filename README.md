# Galaxy Server on SURF ResearchCloud

This repo provides the Ansible playbook for a [Galaxy](https://galaxyproject.org/) server component on SURF ResearchCloud (SRC).

### Roles used

* The official [Galaxy Ansible role](https://github.com/galaxyproject/ansible-galaxy)
* The official [Galaxy postgres](https://github.com/galaxyproject/ansible-postgresql) and [postgres_objects](https://github.com/galaxyproject/ansible-postgresql-objects) roles for database management
* Utility roles from the [UU SRC collection](https://github.com/UtrechtUniversity/researchcloud-items).
* Assumes Nginx is already installed on the workspace (via the SURF Nginx component)
 
## Overview

### Services

* Postgres is installed on the same host as Galaxy
* Galaxy is started the first time via `/usr/local/bin/galaxyctl start`. After that, it can be managed using `systemctl`, e.g. with `systemctl status galaxy.target`.
* An Nginx reverse proxy is started serving the Galaxy application on `https://<workspace_fqdn>`, providing SRAM authentication (see below).

**Note: when starting the workspace, the webserver comes up before the Galaxy application has fully started. This may result in an '502 Bad Gateway' error displayed in your browser.** If this happens, just try again a minute or two later! (Todo is to give a more useful error message to the user).

### Authentication

Galaxy is configured to let the webserver (Nginx) handle authentication. The webserver uses openid to authenticate against SRAM.

Any members of the workspace's Collaborative Organisation (CO) will be able to authenticate using the authentication mechanism of their institution (Single Sign-On).

Galaxy is configured such that members of the CO that are in the SRAM workspace admin group (`src_co_admin`) will be Galaxy administrators. Other users are normal users.

### ResearchCloud parameters

The component takes the following parameters:

* `src_galaxy_version`: set to e.g. `23.0` (default) to control the version of Galaxy that will be installed.
* `src_galaxy_storage_path`: **Interactive parameter**. Default: `/srv/galaxy/datadir`. Path where Galaxy's "mutable data directory" will be located, including the following files:

```
# ls /srv/galaxy/datadir/
cache  config  datasets  dependencies  gravity  jobs  log  shed_tools  tool_data
```

If you attach additional networked storage to the workspace, you can set `src_galaxy_storage_path` to a path on that storage volume. If your storage is e.g. called "galaxy storage", set the parameter to: `/data/galaxy_storage/datadir`. In theory, this should allow you to re-use datasets, tools, etc. from previous Galaxy workspaces.

