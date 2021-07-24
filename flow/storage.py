from dataclasses import dataclass
from datetime import datetime
import json
from typing import Optional

from telegram.message import Message

from .database import Database


@dataclass
class Post:
    channel_name: str
    is_published: int
    date_added: datetime
    photos: list[str]
    vk_post_id: int  # primary key
    vk_post_date: datetime
    vk_group_id: int
    content: Optional[str] = None
    tg_post_ids: Optional[str] = None
    tg_post_date: Optional[datetime] = None
    tg_chat_id: Optional[int] = None


class Storage:
    def __init__(self, db: Database):
        self.db = db

    def get_existing_posts_vk_post_ids(self, vk_post_ids: list[int]):
        query = "".join(
            [
                """
            SELECT vk_post_id
            FROM post
            WHERE vk_post_id IN (
                """,
                ",".join("?" * len(vk_post_ids)),
                ")",
            ]
        )
        return [d["vk_post_id"] for d in self.db.execute(query, vk_post_ids).fetchall()]

    def add_post(self, post: Post):
        post_d = post.__dict__
        query = f"""
            INSERT INTO post (
                {",".join(post_d.keys())}
            )
            VALUES (
                {", ".join("?" * len(post_d))}
            )
        """

        post_d["photos"] = json.dumps(post_d["photos"])
        self.db.execute(query, list(post_d.values()))
        self.db.commit()

    def get_unpublished_posts(self, channel_name: str, limit: Optional[int]):
        query = """
            SELECT * FROM post
            WHERE is_published = 0 AND
                  channel_name = ?
            ORDER BY vk_post_date DESC
        """
        params = [channel_name]
        if limit:
            query += "\nLIMIT ?"
            params.append(str(int(limit)))
        posts = self.db.execute(query, params).fetchall()
        for d in posts:
            d["photos"] = json.loads(d["photos"])
        return [Post(**d) for d in posts]

    def mark_post_as_published(self, vk_post_id: int, tg_sent_posts: list[Message]):
        tg_post_ids = []
        if tg_sent_posts:
            for post in tg_sent_posts:
                msg_id: int = post.message_id
                tg_post_ids.append(msg_id)

            last_post = tg_sent_posts[-1]
            tg_post_date: datetime = last_post.date
            tg_chat_id = last_post.chat_id
        else:
            tg_post_date, tg_chat_id = datetime.now(), ""

        query = """
            UPDATE post
            SET is_published = 1,
                tg_post_ids = ?,
                tg_post_date = ?,
                tg_chat_id = ?
            WHERE vk_post_id = ?
        """
        self.db.execute(
            query, (json.dumps(tg_post_ids), tg_post_date, tg_chat_id, vk_post_id)
        )
        self.db.commit()

    def mark_all_posts_as_published_for_channel(self, channel_name: str):
        self.db.execute(
            """
            UPDATE post
            SET is_published = 1
            WHERE channel_name = ?
        """,
            (channel_name,),
        )
        self.db.commit()
