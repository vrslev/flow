import os
import sqlite3
from typing import Any, Optional, Union


def _dict_factory(cursor: sqlite3.Cursor, row: sqlite3.Row):
    d: dict[str, Any] = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class Database:
    con: Optional[sqlite3.Connection] = None  # type: ignore

    def __init__(self, fpath: str):
        self.fpath = fpath
        if not os.path.exists(self.fpath):
            open(fpath, "a+")
            self.executescript(SCHEMA)

    def connect(self):
        if not self.con:
            self.con: sqlite3.Connection = sqlite3.connect(
                self.fpath,
                detect_types=sqlite3.PARSE_DECLTYPES,
            )
            self.con.row_factory = _dict_factory

    def execute(self, *args: Any):
        self.connect()
        return self.con.execute(*args)

    def commit(self):
        self.connect()
        self.con.commit()

    def close(self):
        if self.con:
            self.con.close()

    def executescript(self, __sql_script: Union[bytes, str]):
        self.connect()
        return self.con.executescript(__sql_script)


SCHEMA = """
DROP TABLE IF EXISTS post;
CREATE TABLE post (
    channel_name TEXT NOT NULL,
    is_published INT NOT NULL DEFAULT 0 CHECK (is_published IN (0, 1)),
    date_added TIMESTAMP NOT NULL DEFAULT (datetime('now', 'localtime')),
    content TEXT,
    photos TEXT,
    vk_post_id INT NOT NULL PRIMARY KEY,
    vk_post_date TIMESTAMP NOT NULL,
    vk_group_id INT NOT NULL,
    tg_post_ids TEXT,
    tg_post_date TIMESTAMP,
    tg_chat_id INT
);
"""
