import datetime
import json

from libcloud.common.base import ConnectionKey, JsonResponse
from libcloud.common.types import ProviderError
from libcloud.compute.base import KeyPair, Node, NodeDriver, NodeImage, NodeLocation, NodeState
from libcloud.dns.base import DNSDriver, Zone
from libcloud.utils.publickey import get_pubkey_openssh_fingerprint
from libcloud.utils.py3 import httplib


class VscaleJsonResponse(JsonResponse):
    def parse_error(self):
        body = super().parse_error()
        http_code = int(self.status)

        if http_code in (httplib.CONFLICT, httplib.NOT_FOUND):
            raise ProviderError(value=body["error"], http_code=http_code, driver=self)

        return body["error"]


class VscaleConnection(ConnectionKey):
    responseCls = VscaleJsonResponse
    host = "api.vscale.io"

    def add_default_headers(self, headers):
        headers["X-Token"] = self.key
        return headers


class VscaleDriver(NodeDriver):
    connectionCls = VscaleConnection
    name = "Vscale"
    website = "https://vscale.io/"

    NODE_STATE_MAP = {
        "started": NodeState.RUNNING,
        "stopped": NodeState.STOPPED,
        "billing": NodeState.SUSPENDED,
        "queued": NodeState.PENDING,  # в документации нет, но в API возвращает
    }

    def list_locations(self):
        response = self.connection.request("api/datacenter")
        country = {
            1: "RU",
            2: "CH",
            3: "GB",
            5: "RU",
            8: "RU",
            9: "RU",
            10: "RU",
            21: "DE",
        }

        locations = []
        for loc in response.object["datacenters"]:
            locations.append(NodeLocation(loc["id"], loc["name"], country[loc["id"]], self))
        return locations

    def list_images(self):
        images = []
        response = self.connection.request("api/os")
        for image in response.object["os"]:
            images.append(NodeImage(image["Id"], image["Name"], self))
        return images

    def list_size(self):
        pass

    def list_key_pairs(self):
        response = self.connection.request("v1/sshkeys")
        key_pairs = []
        for kp in response.object:
            key_pair = KeyPair(
                name=kp["name"],
                public_key=kp["key"],
                fingerprint=get_pubkey_openssh_fingerprint(kp["key"]),
                driver=self,
                extra=dict(id=kp["id"]),
            )
            key_pairs.append(key_pair)
        return key_pairs

    def get_key_pair(self, key_name):
        key_pairs = self.list_key_pairs()
        for kp in key_pairs:
            if kp.name == key_name:
                return kp
        return None

    def list_nodes(self):
        response = self.connection.request("v1/scalets")
        nodes = []
        for n in response.object:

            state = self.NODE_STATE_MAP.get(n["status"], NodeState.UNKNOWN)

            created = datetime.datetime.strptime(n["created"], "%d.%m.%Y %H:%M:%S")

            private_ips = []
            if n["private_address"]:
                private_ips.append(n["private_address"]["address"])

            public_ips = []
            if n["public_address"]:
                public_ips.append(n["public_address"]["address"])

            # неправильно передаётся name. для сравнения используется поле id
            image = NodeImage(n["made_from"], name=n["made_from"], driver=self)

            node = Node(
                id=n["ctid"],
                name=n["name"],
                state=state,
                public_ips=public_ips,
                private_ips=private_ips,
                driver=self,
                image=image,
                extra=n,
                created_at=created,
            )
            nodes.append(node)

        return nodes


class VscaleDns(DNSDriver):
    connectionCls = VscaleConnection
    name = "Vscale"
    website = "https://vscale.io/"

    def get_zone(self, domain_id) -> Zone:
        response = self.connection.request(f"v1/domains/{domain_id}")

        result = response.object

        zone_id = result.pop("id")
        name = result.pop("name")
        extra = result

        zone = Zone(
            id=zone_id,
            domain=name,
            type="master",
            ttl=None,
            driver=self,
            extra=extra,
        )

        return zone

    def list_zones(self):
        response = self.connection.request("v1/domains/")
        zones = []
        for n in response.object:
            extra = dict(
                tags=n["tags"],
                create_date=n["create_date"],
                cheange_date=n["change_date"],
                user_id=n["user_id"],
            )
            zone = Zone(
                id=n["id"],
                domain=n["name"],
                type="master",
                ttl=None,
                driver=self,
                extra=extra,
            )
            zones.append(zone)
        return zones

    def create_zone(self, domain, type="master", ttl=None, extra=None) -> Zone:
        payload = {"name": domain}
        data = json.dumps(payload)
        headers = {"Content-Type": "application/json"}
        response = self.connection.request("v1/domains/", data=data, headers=headers, method="POST")

        result = response.object

        zone_id = result.pop("id")
        name = result.pop("name")
        extra = result

        zone = Zone(
            id=zone_id,
            domain=name,
            type="master",
            ttl=None,
            driver=self,
            extra=extra,
        )

        return zone
