import re
import textwrap

import markupsafe
from base_telegram_bot import BaseTelegramBot, TelegramBotError
from pydantic import HttpUrl

from flow.models import Post


def _format_internal_vk_links(text: str):
    # [(scheme)?(domain)?(user_id)|(username)] -> \
    # <a href="https://vk.com/(user_id)">(username)</a>
    if match := re.findall(r"\[(https://)?(vk.com/)?([^\|\]]+)\|([^\]]+)\]", text):
        for scheme, domain, user_id, username in match:
            text = text.replace(
                f"[{scheme}{domain}{user_id}|{username}]",
                f'<a href="https://vk.com/{user_id}">{username}</a>',
            )
    return text


def _strip_html_tags(text: str) -> str:
    return markupsafe.Markup(text).striptags()


class Bot(BaseTelegramBot):
    def send_message(self, *, chat_id: int, text: str):
        for chunk in textwrap.wrap(
            text=text,
            width=4096,  # MAX_MESSAGE_LENGTH, taken from python-telegram-bot constants
            replace_whitespace=False,
        ):
            chunk = _strip_html_tags(chunk)
            chunk = _format_internal_vk_links(chunk)
            self.make_request(
                method="/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": chunk,
                    "parse_mode": "HTML",
                },
            )

    def send_photo_group(self, *, chat_id: int, photo_urls: list[HttpUrl]):
        data = {
            "chat_id": chat_id,
            "media": [{"type": "photo", "media": url} for url in photo_urls],
        }
        # Sometimes this endpoint fails for with 400 Bad Request.
        # It is irrelevant to the _request_ though.
        # So, retry three times or give up.
        for _ in range(3):
            try:
                self.make_request(method="/sendMediaGroup", json=data)
                return
            except TelegramBotError as exc:
                if exc.response.status_code != 400:
                    raise


def publish_post(*, token: str, chat_id: int, post: Post):
    bot = Bot(token)
    if post.text:
        bot.send_message(chat_id=chat_id, text=post.text)
    if post.photos:
        bot.send_photo_group(chat_id=chat_id, photo_urls=post.photos)
