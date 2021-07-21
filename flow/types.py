from dataclasses import dataclass
from datetime import datetime
from typing import Optional, TypedDict

JSONString = str


class Post(TypedDict):
    channel_name: str
    is_published: int
    date_added: datetime
    content: Optional[str]
    photos: JSONString  # optional but always encoded
    vk_post_id: int  # primary key
    vk_post_date: datetime
    vk_group_id: int
    tg_post_ids: Optional[str]
    tg_post_date: Optional[datetime]
    tg_chat_id: Optional[int]


class ConfChannel(TypedDict):
    name: str
    tg_chat_id: int
    vk_group_id: int


@dataclass
class Conf:
    channels: list[ConfChannel]
    database: str
    telegram_bot_token: str
    telegram_bot_username: str
    vk_app_id: int
    vk_app_service_token: str
