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
