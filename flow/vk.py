from datetime import datetime
import json
from typing import Any, Union

import click
import vk_api

from .config import conf, config_required, get_channel
from .database import db
from .types import ConfChannel, Post

VK_API_VERSION = "5.131"


def get_vk():
    vk_session = vk_api.VkApi(
        app_id=conf.vk_app_id,
        token=conf.vk_app_service_token,
        api_version=VK_API_VERSION,
    )
    return vk_session.get_api()


def fetch_wall(owner_id: int):
    wall: dict[str, Any] = get_vk().wall.get(owner_id=owner_id)
    return wall


def parse_wall(wall: dict[str, Any], channel: ConfChannel):
    posts: list[Post] = []

    items = wall.get("items", [])
    click.echo(f"Got {len(items)} posts")
    for d in items:
        if d.get("marked_as_ads"):
            continue

        post: Post = {
            "channel_name": channel["name"],
            "is_published": 0,
            "date_added": datetime.now(),
            "content": d["text"],
            "photos": "",
            "vk_post_id": d["id"],
            "vk_post_date": datetime.utcfromtimestamp(d["date"]),
            "vk_group_id": d["owner_id"],
            "tg_post_ids": None,
            "tg_post_date": None,
            "tg_chat_id": channel["tg_chat_id"],
        }

        photos = []
        video_in_post = False
        for att in d.get("attachments", []):
            if att["type"] != "photo":  # TODO: Accept videos
                if att["type"] == "video":
                    video_in_post = True
                continue  # TODO: Log this

            sizes: dict[str, Union[str, int]] = {}
            for s in att["photo"]["sizes"]:
                pixels_count = s["height"] * s["width"]
                if pixels_count in sizes:
                    continue
                sizes[pixels_count] = s["url"]

            max_resolution = max(sizes.keys())
            photos.append(sizes[max_resolution])

        post["photos"] = json.dumps(photos)

        if video_in_post and not post["photos"]:  # TODO: Test this; upd: not working!
            continue

        posts.append(post)

    return posts


def add_posts_to_db(posts: list[Post]):
    # TODO: Fix security
    exist = db.execute(  # nosec
        f"""
        SELECT vk_post_id FROM post
        WHERE vk_post_id IN ({','.join('?' * len(posts))})
    """,
        [d["vk_post_id"] for d in posts],
    ).fetchall()
    exist = [d["vk_post_id"] for d in exist]

    count = 0
    for d in posts:
        keys_to_delete: list[Any] = []
        for k, v in d.items():
            if not k or not v:
                keys_to_delete.append(k)
        for k in keys_to_delete:
            d.pop(k)
        if d["vk_post_id"] in exist:
            continue
        else:
            count += 1
        # TODO: Fix security
        db.execute(  # nosec
            f"""
            INSERT INTO post (
                {','.join(d.keys())}
            ) VALUES ({','.join([f"'{d}'" for d in d.values()])})
        """
        )

    click.echo(f"{count} new posts")
    db.commit()


@config_required
def fetch(channel_name: str):
    click.echo("Retrieving news...")
    channel = get_channel(channel_name)
    wall = fetch_wall(owner_id=channel["vk_group_id"])
    posts = parse_wall(wall, channel)
    add_posts_to_db(posts)
    click.echo("Done.")
