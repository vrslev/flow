import os
from datetime import datetime

import boto3
import botocore.exceptions
import py
import pytest
import sentry_sdk
from sqlmodel import Session, select

import flow.main
from flow.db import Storage
from flow.main import _init_sentry, lambda_handler, main
from flow.models import LambdaSettings, Post, PostDB, Settings


def test_sentry_initialised(monkeypatch: pytest.MonkeyPatch):
    called = False

    def init(dsn: str):
        nonlocal called
        called = True
        assert dsn == "mydsn"

    monkeypatch.setattr(sentry_sdk, "init", init)
    monkeypatch.setenv("SENTRY_DSN", "mydsn")

    _init_sentry()
    assert called


def test_sentry_not_initialised(monkeypatch: pytest.MonkeyPatch):
    called = False

    def init(dsn: str):
        nonlocal called
        called = True  # pragma: no cover
        assert dsn == "mydsn"  # pragma: no cover

    monkeypatch.setattr(sentry_sdk, "init", init)

    _init_sentry()
    assert not called


@pytest.fixture
def settings(monkeypatch: pytest.MonkeyPatch, tmpdir: py.path.local):
    db_path = os.path.join(tmpdir, "database.db")
    monkeypatch.setenv("VK_TOKEN", "my_vk_token")
    monkeypatch.setenv("VK_OWNER_ID", "1")
    monkeypatch.setenv("TG_TOKEN", "my_tg_token")
    monkeypatch.setenv("TG_CHAT_ID", "my_tg_chat_id")
    monkeypatch.setenv("TG_CHAT_ID", "2")
    monkeypatch.setenv("DB_PATH", db_path)
    return Settings()  # type: ignore


def test_main_main(monkeypatch: pytest.MonkeyPatch, settings: Settings):
    called_get_wall = False

    datetime_0 = datetime.now()
    datetime_1 = datetime.now()
    datetime_2 = datetime.now()

    def get_wall(*, token: str, owner_id: int):
        nonlocal called_get_wall
        called_get_wall = True
        assert token == settings.vk_token
        assert owner_id == settings.vk_owner_id
        return [
            Post(id=2, text="text 2", photos=[], date=datetime_2),
            Post(id=1, text="text 1", photos=[], date=datetime_1),
            Post(id=0, text="text 0", photos=[], date=datetime_0),
        ]

    called_publish_post = False
    published_post_ids: list[int] = []

    def publish_post(*, token: str, chat_id: int, post: Post):
        nonlocal called_publish_post
        called_publish_post = True
        assert token == settings.tg_token
        assert chat_id == settings.tg_chat_id
        published_post_ids.append(post.id)

    storage = Storage(settings.db_path)
    storage.add_post(2)

    monkeypatch.setattr(flow.main, "get_wall", get_wall)
    monkeypatch.setattr(flow.main, "publish_post", publish_post)

    assert main(settings.copy()) == 0
    assert called_get_wall
    assert called_publish_post
    assert published_post_ids == [1]

    called_get_wall = False
    called_publish_post = False
    published_post_ids = []

    assert main(settings.copy()) == 0
    assert called_get_wall
    assert called_publish_post
    assert published_post_ids == [0]

    with Session(storage.engine) as session:
        assert [post.id for post in session.exec(select(PostDB))] == [0, 1, 2]


@pytest.fixture
def lambda_settings(monkeypatch: pytest.MonkeyPatch, settings: Settings):
    # Other env vars loaded from "settings" fixture
    monkeypatch.setenv("S3_BUCKET", "my_bucket")
    monkeypatch.setenv("S3_KEY", "my_key")
    monkeypatch.setenv("S3_ENDPOINT", "my_endpoint")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "my_key")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "my_access_key")
    return LambdaSettings()  # type: ignore


@pytest.mark.parametrize("fail_download", (True, False))
def test_lambda_handler(
    monkeypatch: pytest.MonkeyPatch,
    lambda_settings: LambdaSettings,
    fail_download: bool,
):
    calls: list[str] = []

    class MyClient:
        def __init__(
            self,
            service_name: str,
            endpoint_url: str,
            aws_access_key_id: str,
            aws_secret_access_key: str,
        ):
            assert service_name == "s3"
            assert endpoint_url == lambda_settings.s3_endpoint
            assert aws_access_key_id == lambda_settings.aws_access_key_id
            assert aws_secret_access_key == lambda_settings.aws_secret_access_key
            calls.append("init")

        def download_file(self, Bucket: str, Key: str, Filename: str):
            assert Bucket == lambda_settings.s3_bucket
            assert Key == lambda_settings.s3_key
            assert Filename == lambda_settings.db_path
            calls.append("download")
            if fail_download:
                raise botocore.exceptions.ClientError({}, "")

        def upload_file(self, Bucket: str, Key: str, Filename: str):
            assert Bucket == lambda_settings.s3_bucket
            assert Key == lambda_settings.s3_key
            assert Filename == lambda_settings.db_path
            calls.append("upload")

    def main(settings: Settings):
        calls.append("main")

    monkeypatch.setattr(boto3, "client", MyClient)
    monkeypatch.setattr(flow.main, "main", main)

    lambda_handler(None, None)  # type: ignore
    assert calls == ["init", "download", "main", "upload"]
