"""Render templates/galaxy/config/job_conf.yml.j2 through tests/render_job_conf.yml.

Run with:  pytest tests/   (needs ansible-core on PATH, or ANSIBLE_PLAYBOOK=/path/to/ansible-playbook)
"""
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
PLAYBOOK = REPO / "tests" / "render_job_conf.yml"
DUMMY_PASSWORD = "dummy-relay-pass_1.x"


def relay_item(**overrides):
    """One src_galaxy_pulsar_relay_configs item as a dict (dummy credentials only)."""
    item = {
        "name": "srcrelay",
        "relay_url": "https://relay.example.org",
        "relay_username": "galaxy-pulsar",
        "relay_password": DUMMY_PASSWORD,
        "relay_topic_prefix": "src",
        "jobs_directory": "/var/lib/pulsar/staging",
        "docker_enabled": "true",
    }
    item.update(overrides)
    return {k: v for k, v in item.items() if v is not None}


def one_line(items):
    """Format items like the SRC wizard one-line list: [{k: v, k: v}, ...]."""
    return "[" + ", ".join("{" + ", ".join(f"{k}: {v}" for k, v in i.items()) + "}" for i in items) + "]"


class RenderError(Exception):
    pass


def _playbook_bin():
    found = os.environ.get("ANSIBLE_PLAYBOOK") or shutil.which("ansible-playbook")
    if not found:
        pytest.skip("ansible-playbook not found")
    return found


@pytest.fixture
def render(tmp_path):
    def _render(**params):
        dest = tmp_path / "job_conf.yml"
        extra = {"workspace_fqdn": "galaxy.example.org", "render_dest": str(dest)}
        extra.update(params)
        proc = subprocess.run(
            [_playbook_bin(), "-i", "localhost,", "-c", "local", str(PLAYBOOK), "-e", json.dumps(extra)],
            cwd=REPO, capture_output=True, text=True,
        )
        if proc.returncode != 0:
            raise RenderError(proc.stdout + proc.stderr)
        return yaml.safe_load(dest.read_text())
    return _render
