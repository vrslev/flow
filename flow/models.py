from datetime import datetime
from typing import Optional

from pydantic import BaseSettings, HttpUrl
from sqlmodel import Field, SQLModel


class Post(SQLModel):
    id: int
    text: Optional[str]
    photos: list[HttpUrl]
    date: datetime


class PostDB(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)


class Settings(BaseSettings):
    vk_token: str
    vk_owner_id: int
    tg_token: str
    tg_chat_id: int
    db_path: str = "/tmp/database.db"
    sentry_dsn: Optional[str]


class LambdaSettings(Settings):
    s3_bucket: str
    s3_key: str
    s3_endpoint: str
    aws_access_key_id: str
    aws_secret_access_key: str
