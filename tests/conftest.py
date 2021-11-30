import os

import py
import pytest

from flow.models import Settings


# @pytest.fixture(scope="session")
@pytest.fixture
def db_path(tmpdir: py.path.local):
    return os.path.join(tmpdir, "database.db")


@pytest.fixture
def settings(monkeypatch: pytest.MonkeyPatch, db_path: str):
    monkeypatch.setenv("VK_TOKEN", "my_vk_token")
    monkeypatch.setenv("VK_OWNER_ID", "1")
    monkeypatch.setenv("TG_TOKEN", "my_tg_token")
    monkeypatch.setenv("TG_CHAT_ID", "my_tg_chat_id")
    monkeypatch.setenv("TG_CHAT_ID", "2")
    monkeypatch.setenv("DATABASE_PATH", db_path)
    monkeypatch.setenv("DATABASE_PATH", db_path)
    return Settings()
