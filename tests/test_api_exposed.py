"""src_galaxy_api_exposed arrives from ResearchCloud as the string 'true'/'false'.

Pulsar (REST and relay) stages job files through Galaxy's /api/ with a job key, so /api/ must
not be behind SRAM when Pulsar is configured.
"""
import json
import re
import subprocess

import pytest

from conftest import REPO, RenderError, _playbook_bin, one_line, relay_item


def api_auth(**params):
    extra = {"workspace_fqdn": "galaxy.example.org"}
    extra.update(params)
    proc = subprocess.run([_playbook_bin(), "-i", "localhost,", "-c", "local", str(REPO / "tests" / "nginx_api_auth.yml"),
                           "-e", json.dumps(extra)], cwd=REPO, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return re.search(r"API_AUTH=(\w+)", proc.stdout).group(1)


@pytest.mark.parametrize("value,expected", [("true", "noauth"), ("false", "sram"), ("", "noauth")])
def test_api_exposed_string_values(value, expected):
    assert api_auth(src_galaxy_api_exposed=value) == expected


def test_pulsar_requires_exposed_api(render):
    with pytest.raises(RenderError, match="src_galaxy_api_exposed"):
        render(src_galaxy_api_exposed="false", src_galaxy_pulsar_relay_configs=one_line([relay_item()]))


def test_pulsar_with_exposed_api_renders(render):
    render(src_galaxy_api_exposed="true", src_galaxy_pulsar_relay_configs=one_line([relay_item()]))
