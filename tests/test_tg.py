from copy import copy, deepcopy
from datetime import datetime
from types import SimpleNamespace
from typing import Any

import pytest
from base_telegram_bot import TelegramBotError

import flow.tg
from flow.models import Post
from flow.tg import Bot, _format_internal_vk_links, publish_post


@pytest.mark.parametrize(
    ("v", "expected"),
    (
        (
            "[id1|Pavel Durov] is here",
            '<a href="https://vk.com/id1">Pavel Durov</a> is here',
        ),
        ("[vk.com/id1|Pavel Durov]", '<a href="https://vk.com/id1">Pavel Durov</a>'),
        (
            "[https://vk.com/id1|Pavel Durov]",
            '<a href="https://vk.com/id1">Pavel Durov</a>',
        ),
        ("https://vk.com/id1 — Pavel Durov", "https://vk.com/id1 — Pavel Durov"),
    ),
)
def test_format_internal_vk_links(v: str, expected: str):
    assert _format_internal_vk_links(v) == expected


@pytest.fixture
def bot():
    return Bot("tg_token")


def test_bot_send_message(monkeypatch: pytest.MonkeyPatch, bot: Bot):
    count = 0

    def make_request(method: str, json: Any = None, model: Any = None) -> Any:
        assert method == "/sendMessage"
        assert json["parse_mode"] == "HTML"
        assert json["chat_id"] == 1

        nonlocal count
        if count == 0:
            assert len(json["text"]) == 4096
        else:
            assert len(json["text"]) == 1
        count += 1

    called = False

    def mock_format_internal_vk_links(text: str):
        nonlocal called
        called = True
        return text

    monkeypatch.setattr(
        flow.tg, "_format_internal_vk_links", mock_format_internal_vk_links
    )
    bot.make_request = make_request
    bot.send_message(chat_id=1, text="t" * 4097)
    assert called


def test_bot_send_media_group_200_ok(bot: Bot):
    photo_urls = ["https://example.com/image1.jpg", "https://example.com/image2.jpg"]

    def make_request(method: str, json: Any = None, model: Any = None) -> Any:
        assert method == "/sendMediaGroup"
        assert json["chat_id"] == 1
        assert json["media"] == [{"type": "photo", "media": url} for url in photo_urls]

    bot.make_request = make_request
    bot.send_photo_group(chat_id=1, photo_urls=deepcopy(photo_urls))  # type: ignore


@pytest.mark.parametrize("return_on", (1, 2, 3, 4))
def test_bot_send_media_group_400_ok(bot: Bot, return_on: int):
    count = 0

    def make_request(method: str, json: Any = None, model: Any = None) -> Any:
        nonlocal count
        count += 1

        if count == return_on:
            return
        raise TelegramBotError(response=SimpleNamespace(status_code=400))  # type: ignore

    bot.make_request = make_request
    bot.send_photo_group(chat_id=1, photo_urls=[])

    if return_on == 4:
        assert count == 3
    else:
        assert count == return_on


def test_bot_send_media_group_400_not_ok(bot: Bot):
    def make_request(method: str, json: Any = None, model: Any = None) -> Any:
        raise TelegramBotError(response=SimpleNamespace(status_code=401))  # type: ignore

    bot.make_request = make_request
    with pytest.raises(TelegramBotError):
        bot.send_photo_group(chat_id=1, photo_urls=[])


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
