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
    vk_app_id: int
    vk_app_service_token: str

    instance_path: str


def get_instance_path():
    if os.environ.get("IN_LAMBDA"):
        return "/tmp"
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


def patch_database():
    import boto3
    import botocore.exceptions

    from . import database

    class NewDatabase(database.Database):
        def __init__(self, fpath: str):
            self._s3 = boto3.client(
                service_name="s3", endpoint_url="https://storage.yandexcloud.net"
            )
            try:
                self._s3.download_file(Bucket="flowdb", Key="flowdb", Filename=fpath)
            except botocore.exceptions.ClientError:
                pass

            super().__init__(fpath)

        def commit(self):
            super().commit()
            self._s3.upload_file(Bucket="flowdb", Key="flowdb", Filename=self.fpath)

    database.Database = NewDatabase


def get_conf_from_env():
    return Conf(
        channels=[
            ChannelConf(
                name="main",
                tg_chat_id=int(os.environ["TG_CHAT_ID"]),
                vk_group_id=int(os.environ["VK_GROUP_ID"]),
                format_text=True,
            )
        ],
        database="flow.db",
        tg_bot_token=os.environ["TG_BOT_TOKEN"],
        tg_bot_username=os.environ["TG_BOT_USERNAME"],
        vk_app_id=int(os.environ["VK_APP_ID"]),
        vk_app_service_token=os.environ["VK_APP_SERVICE_TOKEN"],
        instance_path="/tmp",  # nosec
    )


def get_conf():
    if os.environ.get("IN_LAMBDA"):
        patch_database()
        return get_conf_from_env()

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
        if "channels" not in conf_dict:
            conf_dict["channels"] = []
        else:
            conf_dict["channels"] = [ChannelConf(**c) for c in conf_dict["channels"]]
        conf_dict["instance_path"] = instance_path
        return Conf(**conf_dict)
