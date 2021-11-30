import os

import py
import pytest
from sqlmodel import Session

from flow.db import Storage
from flow.models import PostDB


@pytest.fixture
def storage(tmpdir: py.path.local):
    return Storage(os.path.join(tmpdir, "database.db"))


def test_add_post(storage: Storage):
    storage.add_post(20)
    with Session(storage.engine) as session:
        assert session.get(PostDB, 20) is not None


def test_post_in_db_true(storage: Storage):
    storage.add_post(20)
    assert storage.post_in_db(20)


def test_post_in_db_false_not_empty_db(storage: Storage):
    storage.add_post(10)
    assert not storage.post_in_db(20)


def test_post_in_db_false_empty_db(storage: Storage):
    assert not storage.post_in_db(20)
