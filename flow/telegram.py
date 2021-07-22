from datetime import datetime
import json
from textwrap import wrap
from time import sleep
from typing import Any, Optional

import click
import telegram
from telegram.constants import MAX_CAPTION_LENGTH, MAX_MESSAGE_LENGTH
from telegram.files.inputmedia import InputMediaPhoto
from telegram.message import Message

from .config import conf, config_required, get_channel
from .database import db
from .format import format_text
from .types import Post


def get_unpublished_posts_from_db(channel_name: str, limit: int):
    limit_text = f"LIMIT {int(limit)}" if limit > 0 else ""

    # TODO: Fix security
    posts: list[Post] = db.execute(  # nosec
        f"""
        SELECT * FROM post
        WHERE is_published = 0
        AND channel_name = ?
        {limit_text}
    """,
        (channel_name,),
    ).fetchall()
    return posts


def mark_post_as_published(vk_post_id: int, sent_posts: list[Message]):
    tg_post_ids = []
    if sent_posts:
        for post in sent_posts:
            msg_id: int = post.message_id
            tg_post_ids.append(msg_id)
        last_post = sent_posts[-1]
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
    db.execute(query, (json.dumps(tg_post_ids), tg_post_date, tg_chat_id, vk_post_id))
    db.commit()


class CustomBot(telegram.Bot):
    def __init__(
        self,
        chat_id: int,
        *args: Any,
        parse_mode: Optional[str] = None,
        **kwargs: Optional[Any],
    ):
        super().__init__(*args, **kwargs)
        self.chat_id = chat_id
        self.parse_mode = parse_mode or telegram.ParseMode.HTML

    def _message(self, *args: Any, **kwargs: Optional[Any]):  # type: ignore
        def send():
            return super(CustomBot, self)._message(*args, **kwargs)

        try:
            return send()
        except telegram.error.RetryAfter as e:
            seconds: float = e.retry_after + 2
            click.echo(
                f"{telegram.error.RetryAfter.__name__}. "
                f"Sleeping for {seconds} seconds"
            )
            sleep(seconds)
            return send()
        except telegram.error.TimedOut as e:
            # No need to retry because for some reason message still being delivered
            click.echo(
                f"{telegram.error.TimedOut.__name__}{': ' + e.message if e.message else ''}"
            )

    def send_message(self, *args: Optional[Any], **kwargs: Any):  # type: ignore
        def send(text: str):
            return super(CustomBot, self).send_message(
                *args,
                chat_id=self.chat_id,
                text=text,
                parse_mode=self.parse_mode,
                **kwargs,
            )

        content: Optional[str] = kwargs.pop("text")
        if not content:
            raise ValueError("No text provided")

        messages: list[Message] = []
        for chunk in wrap(content, MAX_MESSAGE_LENGTH):
            r = send(chunk)
            messages.append(r)
            click.echo(f"New post: {r.text[:50]}")
        return messages

    def send_photo(self, *args: Optional[Any], **kwargs: Any):  # type: ignore
        def send(caption: Optional[str] = None):
            return super(CustomBot, self).send_photo(
                *args,
                chat_id=self.chat_id,
                parse_mode=self.parse_mode,
                caption=caption,
                **kwargs,
            )

        caption: str = kwargs.pop("caption")
        messages: list[Message] = []

        if len(caption) <= MAX_CAPTION_LENGTH:
            r = send(caption=caption)
            messages.append(r)
            click.echo("New post with photo")

        else:
            messages += self.send_message(text=caption)
            r = send()
            messages.append(r)
            click.echo(f"New photo")

        return messages

    def send_media_group(  # type: ignore
        self, *args: Optional[Any], text: Optional[str] = None, **kwargs: Optional[Any]
    ):
        def send():
            return super(CustomBot, self).send_media_group(
                *args, chat_id=self.chat_id, **kwargs
            )

        r: list[Message] = []
        if text:
            r = self.send_message(text=text)

        try:
            r += send()
            sleep(10)  # prevent flood error
        except telegram.error.TimedOut:
            sleep(1)
        except telegram.error.BadRequest as e:
            if msg := getattr(e, "message", None):
                if msg == "Group send failed":
                    click.echo(
                        f"{telegram.error.BadRequest.__name__}: {msg}. Excepting."
                    )
                else:
                    raise e

        click.echo(f"New photo gallery")
        return r


def publish_post(bot: CustomBot, post: Post, format: bool = True):
    content = post["content"]
    if format:
        content = format_text(content)

    photos: str = post["photos"]
    photos = json.loads(photos)

    if not photos and post["content"]:
        r = bot.send_message(text=content)
    elif photos:
        if len(photos) == 1:
            r = bot.send_photo(photo=photos[0], caption=content)
        else:
            r = bot.send_media_group(
                media=[InputMediaPhoto(media=p) for p in photos],
                disable_notification=True,  # prevent double notification
                timeout=60,
            )
    else:
        r = []

    mark_post_as_published(post["vk_post_id"], r)


@config_required
def publish(channel_name: str, limit: int):
    channel = get_channel(channel_name)

    posts = get_unpublished_posts_from_db(
        channel["name"], limit
    )  # TODO: Allow setting limit on number of posts to publish
    click.echo(f"{len(posts)} posts to publish")
    if len(posts) > 0:
        bot = CustomBot(token=conf.tg_bot_token, chat_id=channel["tg_chat_id"])
        click.echo("Publishing...")
        for d in posts:
            publish_post(bot, d, format=channel["format_text"])
            if len(posts) > 1:
                sleep(2)

    click.echo("Done.")
