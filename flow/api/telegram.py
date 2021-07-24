# pyright: reportIncompatibleMethodOverride=false

import re
from textwrap import wrap
from time import sleep
from typing import Any, Optional

import click
import telegram
from telegram.constants import MAX_CAPTION_LENGTH, MAX_MESSAGE_LENGTH
from telegram.message import Message


class CustomBot(telegram.Bot):
    def __init__(
        self,
        *args: Any,
        parse_mode: Optional[str] = None,
        **kwargs: Optional[Any],
    ):
        super().__init__(*args, **kwargs)
        self.parse_mode = parse_mode or telegram.ParseMode.MARKDOWN

    def _post(self, *args: Any, **kwargs: Optional[Any]):
        def send():
            return super(CustomBot, self)._post(*args, **kwargs)

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

    def send_message(self, *args: Optional[Any], **kwargs: Any):
        def send(text: str):
            return super(CustomBot, self).send_message(
                *args,
                text=text,
                parse_mode=self.parse_mode,
                **kwargs,
            )

        content: Optional[str] = kwargs.pop("text")
        if not content:
            raise ValueError("No text provided")

        messages: list[Message] = []
        for chunk in wrap(content, MAX_MESSAGE_LENGTH, replace_whitespace=False):
            r = send(chunk)
            messages.append(r)

            log_msg = re.sub(r"\s", " ", r.text[:50])  # type: ignore
            click.echo(f"New post: {log_msg}")
        return messages

    def send_photo(self, *args: Optional[Any], **kwargs: Any):
        def send(caption: Optional[str] = None):
            return super(CustomBot, self).send_photo(
                *args,
                parse_mode=self.parse_mode,
                caption=caption,
                **kwargs,
            )

        caption: str = kwargs.pop("caption")
        messages: list[Message] = []

        if caption and len(caption) <= MAX_CAPTION_LENGTH:
            r = send(caption=caption)
            messages.append(r)
            click.echo("New post with photo")

        else:
            if caption:
                messages += self.send_message(chat_id=kwargs["chat_id"], text=caption)
            r = send()
            messages.append(r)
            click.echo(f"New photo")

        return messages

    def send_media_group(
        self, *args: Optional[Any], text: Optional[str] = None, **kwargs: Optional[Any]
    ):
        def send():
            return super(CustomBot, self).send_media_group(*args, **kwargs)

        r: list[Message] = []
        if text:
            r = self.send_message(chat_id=kwargs["chat_id"], text=text)

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
