import os
import sqlite3
from typing import Any

import click

from .config import conf, cur_path, instance_path

db_path: str = os.path.join(instance_path, conf.database)


def dict_factory(cursor: sqlite3.Cursor, row: sqlite3.Row):
    d: dict[str, Any] = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_db():
    db = sqlite3.connect(
        db_path,
        detect_types=sqlite3.PARSE_DECLTYPES,
    )
    db.row_factory = dict_factory
    return db


db = get_db()


def close_db():  # TODO: Not using it
    if db is not None:
        db.close()


def init_db():
    global db
    if os.path.exists(db_path):  # TODO: Not working
        tables = db.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type ='table'
            AND name NOT LIKE 'sqlite_%'
        """
        ).fetchall()
        tables = [d["name"] for d in tables]

        if "post" in tables:
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
                if value == conf.telegram_bot_username:
                    verified = True
                    break

            if not verified:
                return

    else:
        open(db_path, "a+")

    db = get_db()

    with open(os.path.join(cur_path, "schema.sql")) as f:
        db.executescript(f.read())
    click.echo("Database initialised.")
