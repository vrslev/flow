import contextlib
import os
from typing import Any

import boto3
import botocore.exceptions
import sentry_sdk

from flow.db import Storage
from flow.models import LambdaSettings, Settings
from flow.tg import publish_post
from flow.vk import get_wall


def _init_sentry():
    if _sentry_dsn := os.environ.get("SENTRY_DSN"):
        sentry_sdk.init(_sentry_dsn)


_init_sentry()


def main(settings: Settings) -> int:
    storage = Storage(settings.db_path)
    wall = get_wall(token=settings.vk_token, owner_id=settings.vk_owner_id)

    for post in wall:
        if storage.post_in_db(post.id):
            continue
        publish_post(token=settings.tg_token, chat_id=settings.tg_chat_id, post=post)
        storage.add_post(post.id)
        break

    return 0


@contextlib.contextmanager
def db_from_s3(settings: LambdaSettings):
    client = boto3.client(  # type: ignore
        service_name="s3",
        endpoint_url=settings.s3_endpoint,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )
    try:
        client.download_file(
            Bucket=settings.s3_bucket, Key=settings.s3_key, Filename=settings.db_path
        )
    except botocore.exceptions.ClientError:
        # Initial download (object doesn't exist yet)
        pass
    yield
    client.upload_file(
        Bucket=settings.s3_bucket, Key=settings.s3_key, Filename=settings.db_path
    )


def lambda_handler(event: Any, handler: Any):
    settings = LambdaSettings()
    with db_from_s3(settings):
        main(settings)


if __name__ == "__main__":
    settings = Settings(".env")
    raise SystemExit(main(settings))
