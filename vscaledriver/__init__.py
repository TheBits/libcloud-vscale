import datetime
import json
from typing import List, Optional

from libcloud.common.base import ConnectionKey, JsonResponse
from libcloud.common.types import InvalidCredsError, ProviderError
from libcloud.compute.base import KeyPair, Node, NodeDriver, NodeImage, NodeLocation, NodeSize, NodeState
from libcloud.dns.base import DNSDriver, Record, Zone
from libcloud.dns.types import (
    RecordAlreadyExistsError,
    RecordDoesNotExistError,
    RecordError,
    RecordType,
    ZoneDoesNotExistError,
    ZoneError,
)
from libcloud.utils.publickey import get_pubkey_openssh_fingerprint
from libcloud.utils.py3 import httplib


class VscaleJsonResponse(JsonResponse):
    def parse_error(self):
        http_code = int(self.status)
        if http_code == httplib.FORBIDDEN:
            raise InvalidCredsError("Invalid credentials")

        body = super().parse_error()

        if http_code in (httplib.CONFLICT, httplib.NOT_FOUND):
            raise ProviderError(value=body["error"], http_code=http_code)

        return body["error"]

    def success(self):
        # При успешном DELETE возвращается NO CONTENT
        if self.status == httplib.NO_CONTENT:
            return True
        return super().success()


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
            locations.append(
                NodeLocation(loc["id"], loc["name"], country[loc["id"]], self),
            )
        return locations

    def list_images(self):
        images = []
        response = self.connection.request("v1/images")
        for image in response.object:
            images.append(NodeImage(image["id"], image["description"], self, extra=image))
        return images

    def list_sizes(self, location=None):
        sizes = []
        response = self.connection.request("v1/rplans")
        for plan in response.object:
            # since selectel doesnt support filtering do it manually
            if location and location not in plan["locations"]:
                continue
            # selectel doesn't provide prices for plans and bandwidth
            #  so set to 0
            extra = plan
            sizes.append(
                NodeSize(
                    id=plan["id"],
                    name=plan["id"],
                    ram=plan["memory"],
                    disk=plan["disk"],
                    price=0,
                    bandwidth=0,
                    driver=self,
                    extra=extra,
                ),
            )
        return sizes

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

    def create_key_pair(self, name: str, public_key: str) -> KeyPair:
        payload = {
            "key": public_key,
            "name": name,
        }
        data = json.dumps(payload)
        headers = {"Content-Type": "application/json"}
        response = self.connection.request(
            "v1/sshkeys",
            method="POST",
            headers=headers,
            data=data,
        )
        kp = response.object

        key = kp.pop("key")
        key_pair = KeyPair(
            name=kp.pop("name"),
            public_key=key,
            fingerprint=get_pubkey_openssh_fingerprint(key),
            driver=self,
            extra=kp,
        )
        return key_pair

    def delete_key_pair(self, key_pair: KeyPair):
        key_pair_id = key_pair.extra["id"]
        response = self.connection.request(f"v1/sshkeys/{key_pair_id}", method="DELETE")
        return response.status == httplib.NO_CONTENT

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

    RECORD_TYPE_MAP = {
        RecordType.SOA: "SOA",
        RecordType.NS: "NS",
        RecordType.A: "A",
        RecordType.AAAA: "AAAA",
        RecordType.CNAME: "CNAME",
        RecordType.SRV: "SRV",
        RecordType.MX: "MX",
        RecordType.TXT: "TXT",
        RecordType.SPF: "SPF",
    }

    def get_zone(self, domain_id: str) -> Zone:
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
        response = self.connection.request(
            "v1/domains/",
            data=data,
            headers=headers,
            method="POST",
        )

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

    def delete_zone(self, zone) -> bool:
        try:
            response = self.connection.request(f"v1/domains/{zone.id}", method="DELETE")
        except ProviderError as e:
            if e.value == "domain_not_found":
                raise ZoneDoesNotExistError(e.value, self, zone.id)
            raise

        return response.status == httplib.NO_CONTENT

    def list_records(self, zone: Zone) -> List[Record]:
        response = self.connection.request(f"v1/domains/{zone.id}/records/")
        result = response.object

        records = []
        for r in result:
            zone_id = r.pop("id")
            name = r.pop("name")
            record_type = r.pop("type")
            data = r.pop("content")
            ttl = r.pop("ttl", None)
            extra = r

            record = Record(
                id=zone_id,
                name=name,
                type=record_type,
                data=data,
                zone=zone,
                driver=self,
                ttl=ttl,
                extra=extra,
            )
            records.append(record)

        return records

    def get_record(self, zone_id: str, record_id: str):
        response = self.connection.request(f"v1/domains/{zone_id}/records/{record_id}")
        result = response.object

        result_id = str(result.pop("id"))
        name = result.pop("name")
        result_type = result.pop("type")
        data = result.pop("content")
        ttl = result.pop("ttl", None)
        extra = result

        zone = self.get_zone(zone_id)

        record = Record(
            id=result_id,
            name=name,
            type=result_type,
            data=data,
            zone=zone,
            driver=self,
            ttl=ttl,
            extra=extra,
        )
        return record

    def create_record(self, name, zone: Zone, type, data, extra=None):
        payload = {
            "id": zone.id,
            "name": name,
            "type": type,
            "ttl": 604800,
            "content": data,
        }
        data = json.dumps(payload)
        headers = {"Content-Type": "application/json"}
        url = f"v1/domains/{zone.id}/records/"
        try:
            response = self.connection.request(
                url,
                method="POST",
                headers=headers,
                data=data,
            )
        except ProviderError as e:
            if e.value == "record_already_exists":
                raise RecordAlreadyExistsError(e.value, self, record_id=None)
            raise

        result = response.object
        result_id = str(result.pop("id"))
        name = result.pop("name")
        result_type = result.pop("type")
        data = result.pop("content")
        ttl = result.pop("ttl")
        extra = result

        record = Record(
            id=result_id,
            name=name,
            type=result_type,
            data=data,
            zone=zone,
            driver=self,
            ttl=ttl,
            extra=extra,
        )
        return record

    def delete_record(self, record):
        response = self.connection.request(
            f"v1/domains/{record.zone.id}/records/{record.id}",
            method="DELETE",
        )
        return response.status == httplib.NO_CONTENT

    def update_record(
        self,
        record,
        name: Optional[str],
        type: Optional[RecordType],
        data: Optional[str],
        extra=None,
    ):

        payload = {}
        payload["name"] = record.name if name is None else name
        payload["type"] = record.type if type is None else type
        payload["content"] = record.data if data is None else data

        url = f"v1/domains/{record.zone.id}/records/{record.id}"
        headers = {"Content-Type": "application/json"}
        data = json.dumps(payload)
        try:
            response = self.connection.request(
                url,
                method="PUT",
                headers=headers,
                data=data,
            )
        except ProviderError as e:
            if e.value == "domain_not_found":
                raise ZoneDoesNotExistError(e.value, self, record.zone.id)
            if e.value == "record_not_found":
                raise RecordDoesNotExistError(e.value, self, record.id)
            if e.value == "record_already_exists":
                raise RecordAlreadyExistsError(e.value, self, record.id)
            if e.value in (
                "cname_record_conflict",
                "record_does_not_belong_to_domain",
                "cant_add_soa",
                "string_required",
                "bad_zone_name",
                "bad_record_name",
                "zone_name_too_long",
            ):
                raise RecordError(e.value, self, record.id)
            raise

        result = response.object
        result_id = str(result.pop("id"))
        name = result.pop("name")
        result_type = result.pop("type")
        data = result.pop("content")
        ttl = result.pop("ttl")
        extra = result

        record = Record(
            id=result_id,
            name=name,
            type=result_type,
            data=data,
            zone=record.zone,
            driver=self,
            ttl=ttl,
            extra=extra,
        )

        return record

    def update_zone(
        self,
        zone: Zone,
        domain: Optional[str],
        type: Optional[str] = "master",
        ttl: Optional[int] = None,
        extra: Optional[dict] = None,
    ) -> Zone:
        """Обновляет зону"""

        # INFO: TTL и domain нельзя обновить
        # TODO: Сделать warning на TTL и domain

        payload = {}
        if extra:
            payload.update(extra)
        if type is not None:
            payload["type"] = type

        url = f"v1/domains/{zone.id}"
        headers = {"Content-Type": "application/json"}
        data = json.dumps(payload)
        try:
            response = self.connection.request(
                url,
                method="PATCH",
                headers=headers,
                data=data,
            )
        except ProviderError as e:
            if e.value == "domain_not_found":
                raise ZoneDoesNotExistError(e.value, self, zone.id)
            if e.value == "tag_not_found":
                raise ZoneError(e.value, self, zone.id)
            raise

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
