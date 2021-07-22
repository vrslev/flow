import os
import sqlite3
from typing import Any, Optional, Union

import click

from .config import conf, cur_path, instance_path


def dict_factory(cursor: sqlite3.Cursor, row: sqlite3.Row):
    d: dict[str, Any] = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class Database:
    con: Optional[sqlite3.Connection] = None  # type: ignore

    def connect(self):
        if not self.con:
            self.con: sqlite3.Connection = sqlite3.connect(
                db_path,
                detect_types=sqlite3.PARSE_DECLTYPES,
            )
            self.con.row_factory = dict_factory

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


db_path: str = os.path.join(instance_path, conf.database)
db = Database()


def init_db():
    global db

    if not os.path.exists(db_path):
        open(db_path, "a+")
    else:
        tables = db.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type = 'table'
            AND name NOT LIKE 'sqlite_%'
        """
        ).fetchall()
        tables = [d["name"] for d in tables]

        if "post" in tables and db.execute("SELECT * FROM post").fetchone():
            if not click.confirm(
                "This will erase existing database. Do you want to continue?"
            ):
                return

            verified = False
            for i in range(5):
                if i == 0:
                    msg = "Please enter your bot's username"
                else:
                    msg = "Wrong username, try again"
                value = click.prompt(msg)
                if value == conf.tg_bot_username:
                    verified = True
                    break

            if not verified:
                return

    db = Database()
    with open(os.path.join(cur_path, "schema.sql")) as f:
        db.executescript(f.read())
