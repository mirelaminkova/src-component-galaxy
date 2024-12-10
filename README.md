# Galaxy Server on SURF ResearchCloud

This repo provides the Ansible playbook for a [Galaxy](https://galaxyproject.org/) server component on SURF ResearchCloud (SRC) 🏄‍♀️.

### Roles used

* The official [Galaxy Ansible role](https://github.com/galaxyproject/ansible-galaxy)
* The official [Galaxy postgres](https://github.com/galaxyproject/ansible-postgresql) and [postgres_objects](https://github.com/galaxyproject/ansible-postgresql-objects) roles for database management
* The official [Galaxy CVMFS role](https://training.galaxyproject.org/training-material/topics/admin/tutorials/cvmfs/tutorial.html) and [Apptainer](https://training.galaxyproject.org/training-material/topics/admin/tutorials/apptainer/tutorial.html) provided by the Galaxy community
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
Note: only members of the `src_co_admin` group are given permission to install tools on the Galaxy instance.

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

### Connecting to Pulsar 

A Galaxy machine can be connected to Pulsar inside the SRC, following the [SRC component Pulsar](https://github.com/ErasmusMC-Bioinformatics/src-component-pulsar) instructions. 


If you attach additional networked storage to the workspace, you can set `src_galaxy_storage_path` to a path on that storage volume. If your storage is e.g. called "galaxy storage", set the parameter to: `/data/galaxy_storage/datadir`. In theory, this should allow you to re-use datasets, tools, etc. from previous Galaxy workspaces.

