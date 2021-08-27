import os
from time import sleep
from typing import Optional

import click
from telegram.error import BadRequest

from .api.telegram import CustomBot
from .config import ChannelConf, get_conf
from .database import Database
from .storage import Storage
from .telegram import Chat
from .vk import get_vk_updates


class Flow:
    def __init__(self):
        self.conf = get_conf()
        db_path = os.path.join(self.conf.instance_path, self.conf.database)
        self.db = Database(db_path)
        self.storage = Storage(self.db)
        self.bot = CustomBot(token=self.conf.tg_bot_token)

    def fetch(self, channel_name: str):
        channel_conf = self._get_channel_conf(channel_name)
        click.echo(f'Retrieving new posts for channel "{channel_name}"...')
        posts = get_vk_updates(self.conf.vk_app_service_token, channel_conf)

        existing_posts_vk_post_ids = self.storage.get_existing_posts_vk_post_ids(
            [post.vk_post_id for post in posts]
        )

        for post in posts:
            if post.vk_post_id not in existing_posts_vk_post_ids:
                self.storage.add_post(post)

    def publish(
        self,
        channel_name: str,
        post_frequency: int,
        limit: Optional[int] = None,
    ):
        channel_conf = self._get_channel_conf(channel_name)
        chat = Chat(self.bot, channel_conf.tg_chat_id, channel_conf.format_text)
        posts = self.storage.get_unpublished_posts(channel_conf.name, limit)
        click.echo(f"{len(posts)} posts to publish")
        for post in posts:
            try:
                chat.publish_post(post)
            except BadRequest:
                pass
            self.storage.mark_post_as_published(post.vk_post_id, [])
            if len(posts) > 1:
                sleep(post_frequency)

    def _get_channel_conf(self, channel_name: str) -> ChannelConf:
        for c in self.conf.channels:
            if c.name == channel_name:
                return c
        raise ValueError(f'Channel not in config: "{channel_name}"')
