"""The relay topics are named after the *runner's* Pulsar manager, not the destination's.

Pulsar's RelayClientManager (pulsar.client.manager) takes ``manager`` from the kwargs Galaxy's
PulsarJobRunner._pulsar_client_manager_args() builds from the runner parameters, and RelayJobClient
publishes job_setup/job_kill/job_status_request to <prefix>_<topic>_<manager>. A ``manager`` on the
environment is only used by the REST interface, so it must be rendered on the runner.
"""
import os
import subprocess

import pytest

from conftest import one_line, relay_item

PULSAR_PYTHON = os.environ.get("PULSAR_PYTHON", "/opt/pulsar/venv/bin/python")


def _relay(conf):
    return conf["runners"]["pulsar_relay_srcrelay"], conf["execution"]["environments"]["remote_srcrelay"]


def test_manager_is_a_runner_parameter(render):
    conf = render(src_galaxy_pulsar_relay_configs=one_line([relay_item(manager="tenant_a")]))
    runner, env = _relay(conf)
    assert runner.get("manager") == "tenant_a"
    assert "manager" not in env  # ignored by the relay client, would only mislead


def test_default_manager_not_rendered(render):
    conf = render(src_galaxy_pulsar_relay_configs=one_line([relay_item()]))
    runner, env = _relay(conf)
    assert "manager" not in runner  # Pulsar then uses _default_ (no topic suffix)
    assert "manager" not in env


@pytest.mark.skipif(not os.path.exists(PULSAR_PYTHON), reason="Pulsar venv not available")
def test_topics_match_pulsar_server_side(render):
    """Feed the rendered runner params to Pulsar's own client manager and compare with bind_relay's topics."""
    conf = render(src_galaxy_pulsar_relay_configs=one_line([relay_item(manager="tenant_a")]))
    runner, _ = _relay(conf)
    kwargs = {k: runner[k] for k in runner if k == "manager" or k.startswith("relay_")}
    code = (
        "import json,sys\n"
        "from pulsar.client.manager import build_client_manager\n"
        "kw=json.loads(sys.stdin.read())\n"
        "m=build_client_manager(**kw)\n"
        "print(m._make_topic_name('job_setup', m.manager_name))\n"
        "m.shutdown()\n"
    )
    import json
    out = subprocess.run([PULSAR_PYTHON, "-I", "-c", code], input=json.dumps(kwargs),
                         capture_output=True, text=True, check=True).stdout.strip()
    # pulsar.messaging.bind_relay.__make_topic_name(prefix, "job_setup", manager.name) for a Pulsar
    # manager named tenant_a with relay_topic_prefix src:
    assert out == "src_job_setup_tenant_a"
