from libcloud.common.base import ConnectionKey, JsonResponse
from libcloud.compute.base import NodeDriver, NodeImage, NodeLocation


class VscaleConnection(ConnectionKey):
    responseCls = JsonResponse
    host = "api.vscale.io"

    def add_default_headers(self, headers):
        headers["X-Token"] = self.key
        return headers


class VscaleDriver(NodeDriver):
    connectionCls = VscaleConnection
    name = "Vscale"
    website = "https://vscale.io/"

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
