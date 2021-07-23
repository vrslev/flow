from dataclasses import dataclass
import json
from typing import Any
import urllib.parse
import urllib.request

from .. import __version__


@dataclass
class VkApi:
    access_token: str
    api_version: str = "5.131"
    user_agent: str = f"python-flow/{__version__}"

    def __init__(self, access_token: str):
        self.access_token = access_token

    def call_api(self, method: str, **params: Any):
        if not params:
            params = {}
        params |= {
            "access_token": self.access_token,
            "v": self.api_version,
        }
        data = urllib.parse.urlencode(params)
        url: str = f"https://api.vk.com/method/{method}?{data}"

        headers = {"User-Agent": self.user_agent}
        request = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(request).read()  # nosec
        response = json.loads(response)
        if "error" in response:
            err = response["error"]
            raise VkApiError(err["error_code"], err["error_msg"])
        return response["response"]

    def get_wall(self, owner_id: int):
        return self.call_api("wall.get", owner_id=owner_id)

    def get_group_info(self, group_id: str):
        return self.call_api("groups.getById", group_id=group_id)


class VkApiError(Exception):
    ...
