import os

import vcr

from vscaledriver import VscaleDriver


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
