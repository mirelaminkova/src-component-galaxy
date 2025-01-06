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
<<<<<<< HEAD

**Note: when starting the workspace, the webserver comes up before the Galaxy application has fully started. This may result in an '502 Bad Gateway' error displayed in your browser.** If this happens, just try again a minute or two later! (Todo is to give a more useful error message to the user).
=======
  * Nginx proxies port 443 to localhost:8080
* If `src_galaxy_interactive_tools` is enabled, the [gx-it-proxy](https://github.com/galaxyproject/gx-it-proxy) application is started on port `8001`.
* If `src_galaxy_enable_tus`, [`tusd`](https://training.galaxyproject.org/training-material/topics/admin/tutorials/tus/tutorial.html) is started on port `8002`.
>>>>>>> 179eaa5 (Change tusd gx-it-proxy ports.)

### Authentication

Galaxy is configured to let the webserver (Nginx) handle authentication. The webserver uses openid to authenticate against SRAM.

Any members of the workspace's Collaborative Organisation (CO) will be able to authenticate using the authentication mechanism of their institution (Single Sign-On).

Galaxy is configured such that members of the CO that are in the SRAM workspace admin group (`src_co_admin`) will be Galaxy administrators. Other users are normal users.

### ResearchCloud parameters

The component takes the following parameters:

* `src_galaxy_version`: String. Set to e.g. `23.2` (default) to control the version of Galaxy that will be installed.
* `src_galaxy_api_exposed`: Boolean. if `true` (default), the `/api` route does not require authentication via Single Sign-On.
* `src_ibridges`: Boolean (default: `true`). Whether to enable support for the [iBridges](https://github.com/UtrechtUniversity/galaxy-tools-ibridges) tool for connecting to Yoda and iRODS instances. Implies `src_galaxy_bootstrap`, and adds iBridges to the list of tools to be installed automatically.
* `src_galaxy_jobs_default`: String. What runner to use for jobs by default. Valid values: `singularity`, `docker`, `local`.
* `src_galaxy_interactive_tools`: if `true` (default), support for [interactive tools](https://docs.galaxyproject.org/en/master/admin/special_topics/interactivetools.html) is enabled.
* `src_galaxy_co_admin_group`: String group corresponding to an SRAM group. Members of this SRAM group will be made Galaxy admin users.
* `src_galaxy_bootstrap`: if `true` (default), will attempt to install workflows, dataproviders and tools as configured by the following options:
    * `src_galaxy_tool_files`: String of comma-separated paths to YAML files (in this repo) containing tool specifications.
    * `src_galaxy_workflow_files`: String of comma-separated paths to `.ga` files (in this repo) containing workflow specifications.
    * `src_galaxy_custom_repo`: **Interactive parameter**. String URL to a git repo containing workflow files (in the `workflows` dir of the root of the repo) and tool specification files (in the `tools` dir). Example repo: 
    * `src_galaxy_custom_repo_branch`: **Interactive parameter**. String branch of the custom repo to be used.
* `src_galaxy_storage_path`: **Interactive parameter**. Default: `/srv/galaxy/datadir`. Path where Galaxy's "mutable data directory" will be located, including the following files:

If you attach additional networked storage to the workspace, you can set `src_galaxy_storage_path` to a path on that storage volume. If your storage is e.g. called "galaxy storage", set the parameter to: `/data/galaxy_storage/datadir`. In theory, this should allow you to re-use datasets, tools, etc. from previous Galaxy workspaces.

### Bootstrapping

The `src_galaxy_bootstrap` parameter determines whether the Galaxy instance should be bootstrapped: that is, whether various tools, workflows, and datamanagers should be installed.
These can be installed from various sources:

* a git repo containing `.yml` files descibing which tools to install, and `.ga` workflows files
  * example repo here
  * put tool files in the `tools` subdirectory (as defined by the `_galaxy_custom_repo_tool_location` internal variable).
  * put workflow files in the `workflows` subdirectory (as defined by the `_galaxy_custom_repo_workflow_location` internal variable).
  * use `src_galaxy_custom_repo` and `src_galaxy_custom_repo_branch` to define your repository.
* any number of `.yml` tool files found in this repository
  * use `src_galaxy_tool_files` to provide these. For instance, you may set this parameter to `tools/ibridges.yml,tools/foo.yml` to install the tools defined in those locations.
  * see [here](tools/ibridges.yml) for an example
* any number of `.ga` workflow files found in this repository
  * use `src_galaxy_workflow_files` to provide these. For instance, you may set this parameter to `tools/bar.ga` to install that workflow.

By customizing the `src_galaxy_custom_repo`, `src_galaxy_tool_files` and `src_galaxy_workflow_files` parameters, you can thus create different 'flavours' for your Galaxy Catalog Item
that each contain different tools and workflows out of the box.

__Note__: workflow files installed using the bootstrapping procedure will be installed as `public` workflows available to all users on the Galaxy instance!
You can find these under `Data > Workflows` in Galaxy's main menu.

### Bootstrapping: how does it work?

If boostrapping is enabled, this Ansible playbook will:

1. Configure Galaxy to use a bootstrapping API key in `galaxy.conf`.
1. Restart Galaxy.

...and then invoke the [ansible-galaxy-tools role](https://github.com/UtrechtUniversity/ansible-galaxy-tools/) to do the following:

1. Use the bootstrapping API key to import tools.
1. Use the bootstrapping API key to create an admin user.
  * Use an API key belonging to the admin user to import workflows.

If needed Galaxy, is restarted. Finally, the playbook will __always__ remove the bootstrapping API key. 

## Maintenance

You can stop/restart Galaxy using systemctl, e.g.: `<sudo> systemctl restart galaxy.target`. Use e.g. `<sudo> galaxyctl follow` to follow the logs of all Galaxy services.
