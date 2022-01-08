from datetime import datetime, timedelta
from typing import Any

import pytest

import flow.vk
from flow.models import Post
from flow.vk import (
    VKAPI,
    WallGetResponse,
    WallItem,
    WallItemAttachment,
    WallItemAttachmentPhoto,
    WallItemAttachmentPhotoSize,
    _get_photo_with_highest_quality,
    _parse_wall,
    get_wall,
)


def test_vk_get_wall(monkeypatch: pytest.MonkeyPatch):
    class CustomVKAPI(VKAPI):
        def make_request(
            self, *, method: str, params: dict[str, Any], model: Any = None
        ):
            assert method == "wall.get"
            assert params == {"owner_id": 1}
            assert model is WallGetResponse
            return {"foo": "bar"}

    vk = CustomVKAPI("my_vk_token")
    assert vk.get_wall(owner_id=1) == {"foo": "bar"}


def test_get_photo_with_highest_quality():
    photo = WallItemAttachmentPhoto(
        sizes=[
            WallItemAttachmentPhotoSize(
                width=10,
                height=20,
                url="https://example.com/1",  # type: ignore
            ),
            WallItemAttachmentPhotoSize(
                width=40,
                height=30,
                url="https://example.com/2",  # type: ignore
            ),
        ]
    )
    assert _get_photo_with_highest_quality(photo) == "https://example.com/2"


def test_parse_wall():
    exp_datetime_1 = datetime.now()
    exp_datetime_2 = datetime.now() - timedelta(days=10)
    response = WallGetResponse(
        count=20,
        items=[
            WallItem(
                id=1,
                owner_id=1,
                marked_as_ads=1,
                text="",
                attachments=[],
                date=datetime.now(),
            ),
            WallItem(
                id=2,
                owner_id=1,
                marked_as_ads=0,
                text="my text 0",
                attachments=None,
                date=exp_datetime_1,
            ),
            WallItem(
                id=3,
                owner_id=1,
                marked_as_ads=0,
                text="my text 1",
                attachments=[
                    WallItemAttachment(type="not photo", photo=None),
                    WallItemAttachment(
                        type="photo",
                        photo=WallItemAttachmentPhoto(
                            sizes=[
                                WallItemAttachmentPhotoSize(
                                    width=10,
                                    height=20,
                                    url="https://example.com/1",  # type: ignore
                                ),
                                WallItemAttachmentPhotoSize(
                                    width=40,
                                    height=30,
                                    url="https://example.com/2",  # type: ignore
                                ),
                            ]
                        ),
                    ),
                    WallItemAttachment(
                        type="photo",
                        photo=WallItemAttachmentPhoto(
                            sizes=[
                                WallItemAttachmentPhotoSize(
                                    width=10,
                                    height=20,
                                    url="https://example.com/3",  # type: ignore
                                )
                            ]
                        ),
                    ),
                ],
                date=exp_datetime_2,
            ),
        ],
    )
    assert _parse_wall(response) == [
        Post(
            id=3,
            text="my text 1",
            photos=["https://example.com/2", "https://example.com/3"],  # type: ignore
            date=exp_datetime_2,
        ),
        Post(id=2, text="my text 0", photos=[], date=exp_datetime_1),
    ]


mock_response = {
    "response": {
        "count": 10,
        "items": [
            {
                "id": 10431,
                "from_id": 1,
                "owner_id": 1,
                "date": 1647921520,
                "marked_as_ads": 0,
                "post_type": "post",
                "text": "my text message",
                "is_pinned": 1,
                "attachments": [
                    {
                        "type": "photo",
                        "photo": {
                            "album_id": -7,
                            "date": 1637921826,
                            "id": 457242611,
                            "owner_id": -51200237,
                            "has_tags": False,
                            "access_key": "81a199836c6d2df02a",
                            "post_id": 10756,
                            "sizes": [
                                {
                                    "height": 1509,
                                    "url": "https://sun9-6.userapi.com/impg/...",
                                    "type": "m",
                                    "width": 917,
                                },
                                {
                                    "height": 173,
                                    "url": "https://sun9-6.userapi.com/impg/...",
                                    "type": "o",
                                    "width": 10000,
                                },
                            ],
                            "text": "",
                            "user_id": 100,
                        },
                    },
                    {
                        "type": "link",
                        "link": {
                            "url": "https://vk.com",
                            "title": "VK",
                            "description": "VK",
                            "target": "internal",
                        },
                    },
                ],
                "post_source": {"type": "vk"},
                "comments": {"can_post": 1, "count": 0, "groups_can_post": True},
                "likes": {"can_like": 1, "count": 1, "user_likes": 0, "can_publish": 1},
                "reposts": {"count": 25, "user_reposted": 0},
                "views": {"count": 42178},
                "donut": {"is_donut": False},
                "short_text_rate": 0.8,
                "carousel_offset": 0,
                "hash": "some hash",
            }
        ],
    }
}


def test_get_wall(monkeypatch: pytest.MonkeyPatch):
    class CustomVKAPI(VKAPI):
        def get_wall(self, *, owner_id: int) -> Any:
            assert owner_id == 1

            class MockResponse:
                def json(self):
                    return mock_response

            return self.parse_response(
                response=MockResponse(),  # type: ignore
                model=WallGetResponse,  # type: ignore
            )

    monkeypatch.setattr(flow.vk, "VKAPI", CustomVKAPI)
    get_wall(token="my_vk_token", owner_id=1)
