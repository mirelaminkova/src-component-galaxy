"""Galaxy logs in to the relay with relay_username/relay_password (pulsar_relay_client.auth), so
relay_url must use TLS. Plain http is only accepted for a relay on the same host."""
import pytest

from conftest import DUMMY_PASSWORD, RenderError, one_line, relay_item


@pytest.mark.parametrize("url", ["http://relay.example.org", "relay.example.org", "ftp://relay.example.org"])
def test_rejects_non_https(render, url):
    with pytest.raises(RenderError, match="relay_url") as err:
        render(src_galaxy_pulsar_relay_configs=one_line([relay_item(relay_url=url)]))
    assert DUMMY_PASSWORD not in str(err.value)


@pytest.mark.parametrize("url", ["https://relay.example.org", "https://relay.example.org:8443/", "http://localhost:8080",
                                 "http://127.0.0.1:8080"])
def test_accepts(render, url):
    render(src_galaxy_pulsar_relay_configs=one_line([relay_item(relay_url=url)]))
