"""Smoke tests: job_conf.yml renders to valid YAML without Pulsar, and with one relay."""
from conftest import one_line, relay_item


def test_no_pulsar(render):
    conf = render()
    assert set(conf["runners"]) == {"local"}
    assert "handling" not in conf


def test_one_relay(render):
    conf = render(src_galaxy_pulsar_relay_configs=one_line([relay_item()]))
    runner = conf["runners"]["pulsar_relay_srcrelay"]
    assert runner["load"] == "galaxy.jobs.runners.pulsar:PulsarMQJobRunner"
    assert runner["relay_url"] == "https://relay.example.org"
    assert runner["galaxy_url"] == "https://galaxy.example.org"
    env = conf["execution"]["environments"]["remote_srcrelay"]
    assert env["runner"] == "pulsar_relay_srcrelay"
    assert env["default_file_action"] == "remote_transfer"
    assert conf["handling"] == {"assign": ["db-skip-locked"]}
