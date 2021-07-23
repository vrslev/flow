import logging
import os
import re
import time
from typing import Any, Optional

import click
import schedule
import telegram
import vk_api
import yaml

from .config import ChannelConf, get_conf
from .core import Flow
from .vk import VkApi


def patch_echo():
    """Custom `click.echo` to add logging all messages"""
    old_echo = click.echo  # type: ignore

    def custom_click_echo(
        message: Optional[str], *args: Optional[Any], **kwargs: Optional[Any]
    ):
        logging.info(message)
        return old_echo(message=message, *args, **kwargs)

    click.echo = custom_click_echo


patch_echo()


class CustomClickGroup(click.Group):
    """Custom `click.Group` class to add logging all exceptions"""

    def __call__(self, *args: Optional[Any], **kwargs: Optional[Any]) -> Optional[Any]:
        try:
            return self.main(*args, **kwargs)  # type: ignore
        except Exception as e:
            logging.error(e, exc_info=True)
            raise e


@click.group(cls=CustomClickGroup)
def cli():
    ...


def resolve_channels(channel: Optional[str]):
    conf = get_conf()
    if channel == "all" or len(conf.channels) == 1:  # TODO: This seems wrong
        return (d.name for d in conf.channels)
    elif not channel:
        raise ValueError("Enter channel name")
    else:
        return [channel]


@cli.command("fetch", short_help="Fetch latest 20 posts from VK group feed.")
@click.argument("channel", required=False)
def fetch_command(channel: Optional[str]):
    for d in resolve_channels(channel):
        Flow().fetch(d)
    click.echo("Done.")


@cli.command("publish", short_help="Publish posts that not published yet.")
@click.argument("channel", required=False)
@click.option("--limit", "-l", default=0)
@click.option(
    "--post-frequency", default=2, help="Interval between posts. Default: 2s."
)
def publish_command(channel: Optional[str], limit: int, post_frequency: int):
    for d in resolve_channels(channel):
        Flow().publish(d, post_frequency, limit)
    click.echo("Done.")


def run(channel: str, post_frequency: int):
    click.echo(f'Executing repeated task for channel: "{channel}"')
    flow_ = Flow()
    flow_.fetch(channel)
    flow_.publish(channel, post_frequency)


@cli.command("run", short_help="Run 'fetch' and 'publish' perodically.")
@click.argument("channel", required=False)
@click.option(
    "--fetch-interval",
    default=60,
    help="Interval between requests to fetch new posts. Default: 60s.",
)
@click.option(
    "--post-frequency", default=2, help="Interval between posts. Default: 2s."
)
def run_command(
    channel: str, fetch_interval: int, post_frequency: int
):  # TODO: Separate fetching and posting (doesn't make sense now)
    click.echo("Started running.")
    for d in resolve_channels(channel):
        schedule.every(fetch_interval).seconds.do(run, d, post_frequency)
    if (sleep_to := fetch_interval / 6) < 1:
        sleep_to = 1
    while True:
        schedule.run_pending()
        time.sleep(sleep_to)


add_channel_instructions = """To add new channel you need to:
    1. Add your bot (@{}) to Telegram channel
       in which you're planning to repost posts as Administrator

    2. Send any message in this channel.

If you've done that, than hit 'Enter'."""


@cli.command("add-channel", short_help="Add new channel (source + target).")
def add_channel_command():  # TODO: This is messy
    conf = get_conf()
    if not click.confirm(
        add_channel_instructions.format(conf.tg_bot_username), default=True
    ):
        return

    vk_group_id: Optional[int] = None
    for i in range(5):  # type: ignore
        group_url = click.prompt(
            "Enter link to source VK group, for example, 'https://vk.com/vk'"
        )
        screen_name = re.findall(r"vk.com/([^/]+)", group_url)

        if not screen_name:
            click.echo("Not valid VK Group URL. Try again.")
        else:
            screen_name = screen_name[0]
            try:
                group: dict[str, Any] = VkApi(conf.vk_app_service_token).get_group_info(
                    group_id=str(screen_name)
                )[0]
            except vk_api.exceptions.ApiError as e:
                if e.code == 100:
                    click.echo(
                        f"Group with screen name '{screen_name}'"
                        " does not exist. Try again."
                    )
                    continue
                raise e

            click.echo(f'Got group "{group["name"]}"')
            vk_group_id = int(group["id"])
            if not str(vk_group_id).startswith("-"):
                vk_group_id = int(f"-{vk_group_id}")
            break
    if not vk_group_id:
        return

    tg_chat_id = None
    for i in range(5):  # type: ignore
        channel_name = click.prompt(
            "Enter target Telegram channel name, for example, 'Telegram News'",
            type=str,  # type: ignore
        )

        updates = telegram.Bot(conf.tg_bot_token).get_updates()
        for d in updates:
            chat = d.to_dict().get("channel_post", {}).get("chat", None)
            if chat and chat["type"] == "channel" and chat["title"] == channel_name:
                tg_chat_id = chat["id"]
                break

        if tg_chat_id:
            click.echo(f"Got channel: '{channel_name}'")
            break
        else:
            click.echo(
                "Couldn't get the channel. Make sure you did everything "
                "right and try again."
            )
    if not tg_chat_id:
        return

    channels_in_conf = [d.name for d in conf.channels]
    name = None
    for i in range(5):  # type: ignore
        name = click.prompt('Enter name, for example, "cute_dogs"')

        if name in channels_in_conf:
            click.echo("Channel with this name already in 'config.yaml'. Try again.")
        elif len(re.findall(r"[^a-z0-9_]+", name)) > 0:
            click.echo("Can except only this symbols: a-z, 0-9, _. Try again.")
        else:
            break
    if not name:
        return

    with open(os.path.join(conf.instance_path, "config.yaml"), "r+") as f:
        conf_content = yaml.safe_load(f)
        if "channels" not in conf_content:
            conf_content["channels"] = []

        channel_conf = ChannelConf(
            name=name, format_text=True, tg_chat_id=tg_chat_id, vk_group_id=vk_group_id
        )
        conf_content["channels"].append(channel_conf)

        f.seek(0)
        yaml.dump(conf_content, f, sort_keys=True, indent=2)


@cli.command("list-channels", short_help="Show channels in 'config.yaml'.")
def list_channels_command():
    conf = get_conf()
    channel_names = [d.name for d in conf.channels]
    channel_names.sort()
    click.echo("\n".join(channel_names))
