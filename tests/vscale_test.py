import datetime
import os

import pytest
import vcr
from libcloud.common.types import InvalidCredsError, ProviderError
from libcloud.compute.base import Node, NodeImage, NodeSize
from libcloud.compute.types import NodeState
from libcloud.dns.base import Record, Zone
from libcloud.dns.types import RecordAlreadyExistsError, RecordDoesNotExistError, RecordType, ZoneDoesNotExistError, ZoneError

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


@vcr.use_cassette("./tests/fixtures/list_sizes.yaml", filter_headers=["X-Token"])
def test_list_sizes_no_location():
    conn = VscaleDriver(key=os.getenv("VSCALE_TOKEN"))
    sizes = conn.list_sizes()
    size = sizes.pop()
    assert size.id == "monster"
    assert size.disk == 81920
    assert size.ram == 8192
    assert size.extra["id"] == "monster"


@vcr.use_cassette("./tests/fixtures/list_sizes.yaml", filter_headers=["X-Token"])
def test_list_sizes_with_location_filtering():
    conn = VscaleDriver(key=os.getenv("VSCALE_TOKEN"))
    sizes = conn.list_sizes(location="msk0")
    size = sizes.pop()
    assert size.id == "monster"
    assert size.disk == 81920
    assert size.ram == 8192
    assert size.extra["id"] == "monster"


@vcr.use_cassette("./tests/fixtures/list_images.yaml", filter_headers=["X-Token"])
def test_list_images():
    conn = VscaleDriver(key=os.getenv("VSCALE_TOKEN"))
    keys = conn.list_images()
    key = keys.pop()
    assert key.id == "debian_11_64_001_master"
    assert key.name == "Debian_11_64_001_master"


@vcr.use_cassette("./tests/fixtures/list_locations.yaml", filter_headers=["X-Token"])
def test_list_locations():
    conn = VscaleDriver(key=os.getenv("VSCALE_TOKEN"))
    keys = conn.list_locations()
    key = keys.pop()
    assert key.id == "msk0"
    assert key.name == ""
    assert key.country == "RU"
    assert key.extra["id"] == "msk0"


@vcr.use_cassette("./tests/fixtures/get_key_pair.yaml", filter_headers=["X-Token"])
def test1_get_key_pair():
    conn = VscaleDriver(key=os.getenv("VSCALE_TOKEN"))
    key = conn.get_key_pair("x200s")
    assert key.name == "x200s"
    assert key.fingerprint == "ca:28:dc:6e:9e:72:48:d3:bc:73:76:19:d2:5f:c3:e8"
    assert isinstance(key.driver, VscaleDriver)
    assert key.extra["id"] == 46329


@vcr.use_cassette("./tests/fixtures/compute_get_key_pair.yaml", filter_headers=["X-Token"])
def test_compute_get_key_pair():
    conn = VscaleDriver(key=os.getenv("VSCALE_TOKEN"))
    key = conn.get_key_pair("test key")
    assert key


@vcr.use_cassette("./tests/fixtures/compute_get_key_pair_empty.yaml", filter_headers=["X-Token"])
def test_compute_get_key_pair_empty():
    conn = VscaleDriver(key=os.getenv("VSCALE_TOKEN"))
    key = conn.get_key_pair("MissingName")
    assert key is None


@vcr.use_cassette("./tests/fixtures/compute_delete_key_pair.yaml", filter_headers=["X-Token"])
def test_compute_delete_key_pair():
    conn = VscaleDriver(key=os.getenv("VSCALE_TOKEN"))
    kp = conn.get_key_pair("test key")
    result = conn.delete_key_pair(kp)
    assert result


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
    with pytest.raises(ZoneDoesNotExistError, match="domain_not_found"):
        conn.delete_zone(zone)


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


@vcr.use_cassette("./tests/fixtures/dns_create_record.yaml", filter_headers=["X-Token"])
def test_dns_create_record():
    conn = VscaleDns(key=os.getenv("VSCALE_TOKEN"))
    name = "cloudsea.ru"
    zone = conn.get_zone(name)

    data = "ns3.vscale.io"
    record_type = "NS"
    record = conn.create_record(name, zone, record_type, data)
    records = conn.list_records(zone)

    for r in records:
        if record.id == r.id:
            assert r.name == record.name
            assert r.data == record.data
            break
    else:
        pytest.fail("no record found")


@vcr.use_cassette("./tests/fixtures/dns_delete_record.yaml", filter_headers=["X-Token"])
def test_dns_delete_record():
    conn = VscaleDns(key=os.getenv("VSCALE_TOKEN"))
    name = "cloudsea.ru"
    zone = conn.get_zone(name)

    data = "ns33.vscale.io"
    record_type = "NS"
    record = conn.create_record(name, zone, record_type, data)

    result = conn.delete_record(record)
    assert result

    assert not any(r.data == data for r in zone.list_records())


@vcr.use_cassette("./tests/fixtures/dns_update_record.yaml", filter_headers=["X-Token"])
def test_dns_update_record():
    conn = VscaleDns(key=os.getenv("VSCALE_TOKEN"))
    name = "cloudsea.ru"
    zone = conn.get_zone(name)

    data = "ns20.vscale.io"
    record_type = "NS"
    record = conn.create_record(name, zone, record_type, data)

    update_data = "ns10.vscale.io"
    actual = record.update(data=update_data)

    assert actual.data == update_data
    assert actual.id == record.id

    conn.delete_record(actual)


@vcr.use_cassette("./tests/fixtures/dns_update_record_zone_does_not_exist.yaml", filter_headers=["X-Token"])
def test_dns_update_record_zone_does_not_exist():
    conn = VscaleDns(key=os.getenv("VSCALE_TOKEN"))
    name = "example.com"
    data = "ns10.vscale.io"
    zone = Zone("123", name, "master", ttl=None, driver=conn)
    record = Record("111", name, RecordType.A, data, zone, conn)

    with pytest.raises(ZoneDoesNotExistError, match="domain_not_found"):
        record.update(name=data)


@vcr.use_cassette("./tests/fixtures/dns_update_record_record_does_not_exist.yaml", filter_headers=["X-Token"])
def test_dns_update_record_record_does_not_exist():
    conn = VscaleDns(key=os.getenv("VSCALE_TOKEN"))
    name = "cloudsea.ru"
    zone = conn.get_zone(name)
    record = Record("111", name, RecordType.A, "ns10.vscale.io", zone, conn)

    with pytest.raises(RecordDoesNotExistError):
        conn.update_record(record, name=None, type=None, data=None)


@vcr.use_cassette("./tests/fixtures/dns_create_record_already_exists.yaml", filter_headers=["X-Token"])
def test_dns_create_record_already_exists():
    conn = VscaleDns(key=os.getenv("VSCALE_TOKEN"))
    name = "cloudsea.ru"
    zone = conn.get_zone(name)

    data = "ns15.vscale.io"
    record = conn.create_record(name, zone, RecordType.NS, data)
    with pytest.raises(RecordAlreadyExistsError, match="record_already_exists"):
        conn.create_record(name, zone, RecordType.NS, data)

    record.delete()


@vcr.use_cassette("./tests/fixtures/dns_update_zone.yaml", filter_headers=["X-Token"])
def test_dns_update_zone():
    conn = VscaleDns(key=os.getenv("VSCALE_TOKEN"))
    name = "cloudsea.ru"
    zone = conn.get_zone(name)

    # Теги не созданы
    tags = [1, 2]
    with pytest.raises(ZoneError, match="tag_not_found"):
        conn.update_zone(zone, name, extra=dict(tags=tags))

    result = conn.update_zone(zone, "cloudsea.ru", extra=dict(tags=[]))
    assert result.domain == name


@vcr.use_cassette("./tests/fixtures/compute_create_pair.yaml", filter_headers=["X-Token"])
def test_compute_create_pair():
    conn = VscaleDriver(key=os.getenv("VSCALE_TOKEN"))
    name = "example key"
    public_key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDdlUgMYerMvfRdmMWOSYbbVTkq5kjawV8nwQq0Ify6P user@archlinux"

    kp = conn.create_key_pair(name, public_key)
    assert kp.name == name
    assert kp.public_key == kp.public_key
    assert kp.extra["id"] > 0


@vcr.use_cassette("./tests/fixtures/start_node.yaml", filter_headers=["X-Token"])
def test_start_node():
    conn = VscaleDriver(key=os.getenv("VSCALE_TOKEN"))
    node_id = "123"
    resp = conn.start_node(node_id)
    assert resp is True


@vcr.use_cassette("./tests/fixtures/stop_node.yaml", filter_headers=["X-Token"])
def test_stop_node():
    conn = VscaleDriver(key=os.getenv("VSCALE_TOKEN"))
    node_id = "123"
    resp = conn.stop_node(node_id)
    assert resp is True


@vcr.use_cassette("./tests/fixtures/reboot_node.yaml", filter_headers=["X-Token"])
def test_reboot_node():
    conn = VscaleDriver(key=os.getenv("VSCALE_TOKEN"))
    node = Node(id="123", name="test", state=NodeState.RUNNING, driver=conn, private_ips=[], public_ips=[])
    resp = conn.reboot_node(node)
    assert resp is True


@vcr.use_cassette("./tests/fixtures/create_node.yaml", filter_headers=["X-Token"])
def test_create_node():
    conn = VscaleDriver(key=os.getenv("VSCALE_TOKEN"))
    node_size = NodeSize(id="medium", name="medium", ram=1000, disk=1000, price=100, driver=conn, bandwidth=1000)
    node_image = NodeImage(id="ubuntu_20_04_lts", name="ubuntu_20_04_lts", driver=conn)
    new_node = conn.create_node(name="test_node", size=node_size, image=node_image)
    assert isinstance(new_node, Node)
    assert new_node.id == "11"
    assert new_node.name == "New-Test"
    assert new_node.image == node_image
    assert new_node.created_at == "20.08.2015 14:57:04"
