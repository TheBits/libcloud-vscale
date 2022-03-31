import datetime
import os

import pytest
import vcr
from libcloud.common.types import InvalidCredsError, ProviderError
from libcloud.dns.base import Zone

from vscaledriver import VscaleDns, VscaleDriver


@vcr.use_cassette("./tests/fixtures/list_key_pairs.yaml", filter_headers=["X-Token"])
def test_list_key_pairs():
    conn = VscaleDriver(key=os.getenv("VSCALE_TOKEN"))
    keys = conn.list_key_pairs()
    key = keys.pop()
    assert key.name == "x200s"
    assert key.fingerprint == "ca:28:dc:6e:9e:72:48:d3:bc:73:76:19:d2:5f:c3:e8"
    assert isinstance(key.driver, VscaleDriver)
    assert key.extra["id"] == 46329


@vcr.use_cassette("./tests/fixtures/get_key_pair.yaml", filter_headers=["X-Token"])
def test1_get_key_pair():
    conn = VscaleDriver(key=os.getenv("VSCALE_TOKEN"))
    key = conn.get_key_pair("x200s")
    assert key.name == "x200s"
    assert key.fingerprint == "ca:28:dc:6e:9e:72:48:d3:bc:73:76:19:d2:5f:c3:e8"
    assert isinstance(key.driver, VscaleDriver)
    assert key.extra["id"] == 46329


@vcr.use_cassette("./tests/fixtures/get_key_pair.yaml", filter_headers=["X-Token"])
def test2_get_key_pair():
    conn = VscaleDriver(key=os.getenv("VSCALE_TOKEN"))
    key = conn.get_key_pair("MissingName")
    assert key is None


@vcr.use_cassette("./tests/fixtures/get_key_pair_empty.yaml", filter_headers=["X-Token"])
def test3_get_key_pair():
    conn = VscaleDriver(key=os.getenv("VSCALE_TOKEN"))
    key = conn.get_key_pair("x200s")
    assert key is None


@vcr.use_cassette("./tests/fixtures/list_nodes.yaml", filter_headers=["X-Token"])
def test4_list_nodes():
    conn = VscaleDriver(key=os.getenv("VSCALE_TOKEN"))
    nodes = conn.list_nodes()
    assert nodes

    node1 = nodes[0]
    assert node1.id == "3547397"
    assert node1.created_at == datetime.datetime(2021, 3, 20, 5, 25, 10)
    assert node1.image.id == "ubuntu_20.04_64_001_master"


@vcr.use_cassette("./tests/fixtures/dns_list_zones_empty.yaml", filter_headers=["X-Token"])
def test_dns_list_zones_empty():
    conn = VscaleDns(key=os.getenv("VSCALE_TOKEN"))
    zones = conn.list_zones()
    assert isinstance(zones, list)
    assert not zones


@vcr.use_cassette(
    "./tests/fixtures/dns_list_zones_unauthorized.yaml",
    filter_headers=["X-Token"],
    decode_compressed_response=True,
)
def test5_list_zones_unauthorized():
    conn = VscaleDns(key="key")
    with pytest.raises(InvalidCredsError):
        conn.list_zones()


@vcr.use_cassette("./tests/fixtures/dns_create_zone.yaml", filter_headers=["X-Token"])
def test_dns_create_zone():
    conn = VscaleDns(key=os.getenv("VSCALE_TOKEN"))
    zone = conn.create_zone("cloudsea.ru")
    assert zone
    assert zone.id == "68155"
    assert zone.domain == "cloudsea.ru"
    assert zone.extra == {"user_id": 15872, "tags": [], "change_date": 1648384912, "create_date": 1648384912}


@vcr.use_cassette("./tests/fixtures/dns_create_zone_alread_exist.yaml", filter_headers=["X-Token"])
def test_dns_create_zone_alread_exist():
    conn = VscaleDns(key=os.getenv("VSCALE_TOKEN"))
    with pytest.raises(ProviderError, match="domain_already_exists") as exc_info:
        conn.create_zone("example.com")
    assert exc_info.value.http_code == 409


@vcr.use_cassette("./tests/fixtures/dns_get_zone.yaml", filter_headers=["X-Token"])
def test_dns_get_zone():
    conn = VscaleDns(key=os.getenv("VSCALE_TOKEN"))
    zone = conn.get_zone("cloudsea.ru")
    assert zone
    assert zone.id == "68155"
    assert zone.domain == "cloudsea.ru"
    assert zone.extra == {"user_id": 15872, "tags": [], "change_date": 1648384912, "create_date": 1648384912}


@vcr.use_cassette("./tests/fixtures/dns_get_zone_not_folund.yaml", filter_headers=["X-Token"])
def test_dns_get_zone_not_found():
    conn = VscaleDns(key=os.getenv("VSCALE_TOKEN"))
    with pytest.raises(ProviderError, match="domain_not_found") as exc_info:
        conn.get_zone("example.com")
    assert exc_info.value.http_code == 404


@vcr.use_cassette("./tests/fixtures/dns_delete_zone.yaml", filter_headers=["X-Token"])
def test_dns_delete_zone():
    conn = VscaleDns(key=os.getenv("VSCALE_TOKEN"))
    zone = conn.get_zone("example1.com")
    result = conn.delete_zone(zone)
    assert result


@vcr.use_cassette("./tests/fixtures/dns_delete_zone_not_found.yaml", filter_headers=["X-Token"])
def test_dns_delete_zone_not_found():
    conn = VscaleDns(key=os.getenv("VSCALE_TOKEN"))
    zone = Zone("123", "example.com", "master", ttl=None, driver=conn)
    with pytest.raises(ProviderError, match="domain_not_found") as exc_info:
        conn.delete_zone(zone)
    assert exc_info.value.http_code == 404


@vcr.use_cassette("./tests/fixtures/dns_list_records_example.yaml", filter_headers=["X-Token"])
def test_dns_list_records_example():
    # используется пример из документации
    conn = VscaleDns(key=os.getenv("VSCALE_TOKEN"))
    zone = Zone("123", "example.com", "master", ttl=None, driver=conn)
    records = conn.list_records(zone)
    assert len(records) == 3


@vcr.use_cassette("./tests/fixtures/dns_get_record.yaml", filter_headers=["X-Token"])
def test_dns_get_record():
    conn = VscaleDns(key=os.getenv("VSCALE_TOKEN"))
    zone = conn.get_zone("cloudsea.ru")
    records = conn.list_records(zone)
    reference = records[0]
    record = conn.get_record(zone.id, reference.id)
    assert reference.id == record.id
