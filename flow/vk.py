from datetime import datetime
from typing import Any

import click

from . import __version__
from .api.vk import VkApi
from .config import ChannelConf
from .storage import Post


def get_vk_updates(token: str, channel_conf: ChannelConf):
    wall = VkApi(token).get_wall(channel_conf.vk_group_id)

    posts = _parse_wall(wall, channel_conf.name)
    return posts


def _parse_wall(wall: dict[str, Any], channel_name: str):
    posts: list[Post] = []

    items = wall.get("items", [])
    click.echo(f"Got {len(items)} posts")
    for d in items:
        if d.get("marked_as_ads"):
            continue

        photos: list[str] = []
        video_in_post = False
        for att in d.get("attachments", []):
            if att["type"] != "photo":
                if att["type"] == "video":
                    video_in_post = True
                click.echo(
                    "Skipped attachment with type different from 'photo': "
                    f"'{att['type']}' (group: {d['owner_id']}, post: {d['id']})"
                )
                continue

            sizes: dict[int, str] = {}
            for s in att["photo"]["sizes"]:
                pixels_count = s["height"] * s["width"]
                if pixels_count in sizes:
                    continue
                sizes[pixels_count] = s["url"]

            max_resolution = max(sizes.keys())
            photos.append(sizes[max_resolution])

        post = {
            "channel_name": channel_name,
            "is_published": 0,
            "date_added": datetime.now(),
            "content": d["text"],
            "photos": photos,
            "vk_post_id": d["id"],
            "vk_post_date": datetime.utcfromtimestamp(d["date"]),
            "vk_group_id": d["owner_id"],
        }

        if (video_in_post and not post["photos"]) or not (
            post["content"] and post["photos"]
        ):
            continue

        post = Post(**post)  # type: ignore
        posts.append(post)

    return posts
