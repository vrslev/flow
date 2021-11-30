from copy import copy, deepcopy
from datetime import datetime
from typing import Any

import pytest

import flow.tg
from flow.models import Post
from flow.tg import Bot, publish_post


@pytest.fixture
def bot():
    return Bot("tg_token")


def test_bot_send_message(bot: Bot):
    count = 0

    def make_request(method: str, json: Any = None, model: Any = None) -> Any:
        assert method == "/sendMessage"
        assert json["chat_id"] == 1

        nonlocal count
        if count == 0:
            assert len(json["text"]) == 4096
        else:
            assert len(json["text"]) == 1
        count += 1

    bot.make_request = make_request
    bot.send_message(chat_id=1, text="t" * 4097)


def test_bot_send_media_group(bot: Bot):
    photo_urls = ["https://example.com/image1.jpg", "https://example.com/image2.jpg"]

    def make_request(method: str, json: Any = None, model: Any = None) -> Any:
        assert method == "/sendMediaGroup"
        assert json["chat_id"] == 1
        assert json["media"] == [{"type": "photo", "media": url} for url in photo_urls]

    bot.make_request = make_request
    bot.send_photo_group(chat_id=1, photo_urls=deepcopy(photo_urls))  # type: ignore


def test_publish_post(monkeypatch: pytest.MonkeyPatch):
    exp_token = "my_token"
    exp_text = "my_text"
    exp_photo_urls = [
        "https://example.com/image1.jpg",
        "https://example.com/image2.jpg",
    ]

    class CustomBot:
        def __init__(self, token: str) -> None:
            assert token == exp_token

        def send_message(self, chat_id: int, text: str):
            assert chat_id == 1
            assert text == exp_text

        def send_photo_group(self, chat_id: int, photo_urls: list[str]):
            assert chat_id == 1
            assert photo_urls == exp_photo_urls

    monkeypatch.setattr(flow.tg, "Bot", CustomBot)

    post = Post(
        id=25,
        text=copy(exp_text),
        photos=deepcopy(exp_photo_urls),  # type: ignore
        date=datetime.now(),
    )
    publish_post(token=copy(exp_token), chat_id=1, post=post)
