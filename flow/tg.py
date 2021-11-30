import textwrap

from base_telegram_bot import BaseTelegramBot
from pydantic import HttpUrl

from flow.models import Post

# TODO: Make cli to determine chat id
# TODO: HTML urls


class Bot(BaseTelegramBot):
    def send_message(self, *, chat_id: int, text: str):
        for chunk in textwrap.wrap(
            text=text,
            width=4096,  # MAX_MESSAGE_LENGTH, taken from python-telegram-bot constants
            replace_whitespace=False,
        ):
            self.make_request(
                method="/sendMessage", json={"chat_id": chat_id, "text": chunk}
            )

    def send_photo_group(self, *, chat_id: int, photo_urls: list[HttpUrl]):
        self.make_request(
            method="/sendMediaGroup",
            json={
                "chat_id": chat_id,
                "media": [{"type": "photo", "media": url} for url in photo_urls],
            },
        )


def publish_post(*, token: str, chat_id: int, post: Post):
    bot = Bot(token)
    if post.text:
        bot.send_message(chat_id=chat_id, text=post.text)
    if post.photos:
        bot.send_photo_group(chat_id=chat_id, photo_urls=post.photos)