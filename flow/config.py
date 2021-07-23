from dataclasses import dataclass
import os
import pathlib

import click
import yaml


@dataclass
class ChannelConf:
    name: str
    tg_chat_id: int
    vk_group_id: int
    format_text: bool


@dataclass
class Conf:
    channels: list[ChannelConf]
    database: str
    tg_bot_token: str
    tg_bot_username: str
    vk_app_id: int  # TODO: Do i need this?
    vk_app_service_token: str

    instance_path: str


def get_instance_path():
    var_name = "FLOW_INSTANCE_PATH"
    instance_path = os.environ.get(var_name)
    if not instance_path:
        raise click.UsageError(
            f'You did not provide the "{var_name}" environment variable.'
        )
    elif os.path.exists(instance_path) and os.path.isabs(instance_path):
        return instance_path
    else:
        raise click.UsageError(
            f'Incorrect path set in "{var_name}" environment variable.'
        )


def get_conf():
    instance_path = get_instance_path()

    if not os.path.exists(instance_path):
        os.mkdir(instance_path)

    fpath = os.path.join(instance_path, "config.yaml")

    if not os.path.exists(fpath):
        cur_path = pathlib.Path(__file__).parent
        with open(os.path.join(cur_path, "sample_config.yaml")) as f:
            sample_config = f.read()
        with open(fpath, "a+") as f:
            f.write(sample_config)

    with open(fpath) as f:
        conf_dict = yaml.safe_load(f)
        conf_dict["channels"] = [ChannelConf(**c) for c in conf_dict["channels"]]
        conf_dict["instance_path"] = instance_path
        return Conf(**conf_dict)
