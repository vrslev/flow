import json
import os
import re
import time
from typing import Any, Optional

import click
import schedule
import telegram
import vk_api

from flow.database import init_db
from flow.types import ConfChannel

from .config import conf, instance_path
from .log import CustomClickGroup, logger
from .telegram import publish
from .vk import fetch, get_vk


@click.group(cls=CustomClickGroup)
def cli():
    ...


@cli.command("init-db")
def init_db_command():
    return init_db()


def resolve_channels(channel: Optional[str]) -> list[str]:
    if channel == "all" or len(conf.channels) == 1:
        return [d["name"] for d in conf.channels]
    elif not channel:
        raise ValueError("Enter channel name")
    else:
        return [channel]


@cli.command("fetch")
@click.argument("channel", required=False)
def fetch_command(channel: Optional[str]):
    for d in resolve_channels(channel):
        fetch(d)


@cli.command("publish")
@click.argument("channel", required=False)
def publish_command(channel: Optional[str]):
    for d in resolve_channels(channel):
        publish(d)


def run(channel: str):
    logger.info(f'Executing repeated task for channel: "{channel}"')
    fetch(channel)
    publish(channel)


@cli.command("run")
@click.argument("channel", required=False)
def run_command(channel: str):
    click.echo("Started running.")
    for d in resolve_channels(channel):
        schedule.every(60).seconds.do(run, d)
    while True:
        schedule.run_pending()
        time.sleep(10)


@cli.command("add-channel")
def add_channel_command():
    vk_group_id: Optional[int] = None
    for i in range(5):  # type: ignore
        group_url = click.prompt("Enter source VK Group URL")
        screen_name = re.findall(r"vk.com/([^/]+)", group_url)
        if screen_name:
            screen_name = screen_name[0]
            try:
                group: dict[str, Any] = get_vk().groups.getById(
                    group_id=str(screen_name)
                )[0]
                click.echo(f'Got group "{group["name"]}"')
                vk_group_id = int(group["id"])
                if not str(vk_group_id).startswith("-"):
                    vk_group_id = int(f"-{vk_group_id}")
                break
            except vk_api.exceptions.ApiError as e:
                if e.code == 100:
                    click.echo(f'Group with screen name "{screen_name}" does not exist')
        else:
            click.echo("Not valid VK Group URL. Try again.")

    if not vk_group_id:
        return

    # TODO: Check if config already contain it
    # TODO: Ask for NAME first
    # TODO: Add instructions about telegram channel name: also need to send one message
    # TODO: Unificate all names (config + db)
    tg_chat_id = None
    for i in range(5):  # type: ignore
        channel_name = click.prompt("Enter target Telegram channel name", type=str)  # type: ignore
        bot = telegram.Bot(conf.telegram_bot_token)
        updates = bot.get_updates()
        for d in updates:
            chat = d.to_dict().get("channel_post", {}).get("chat", None)
            if chat and chat["type"] == "channel" and chat["title"] == channel_name:
                tg_chat_id = chat["id"]
                break

        if tg_chat_id:
            click.echo(f'Got channel: "{channel_name}"')
            break
        else:
            click.echo(
                f"Did not get channel. Make sure you did everything right and try again."
            )

    if not tg_chat_id:
        return

    name = None
    for i in range(5):  # type: ignore
        name = click.prompt('Enter name, for example, "cute_dogs"')
        if len(re.findall(r"[^a-z0-9_]+", name)) > 0:
            click.echo("Can except only this symbols: a-z, 0-9, _. Try again.")
        else:
            break

    if not name:
        return

    with open(os.path.join(instance_path, "config.json"), "r+") as f:
        config_content = json.load(f)
        if not config_content.get("channels"):
            config_content["channels"] = []
        channelconf: ConfChannel = {
            "name": name,
            "tg_chat_id": tg_chat_id,
            "vk_group_id": vk_group_id,
        }
        config_content["channels"].append(channelconf)
        f.seek(0)
        json.dump(config_content, f, sort_keys=True, indent=2)


cli.add_command(add_channel_command)
