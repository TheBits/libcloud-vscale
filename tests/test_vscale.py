import datetime
import os

import vcr

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


@vcr.use_cassette("./tests/fixtures/list_zones.yaml", filter_headers=["X-Token"])
def test5_list_zones_empty():
    conn = VscaleDns(key=os.getenv("VSCALE_TOKEN"))
    zones = conn.list_zones()
    assert isinstance(zones, list)
    assert not zones
