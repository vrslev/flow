import json
import os
import pathlib
from typing import Any, Callable

import click

from .types import Conf


class WrongConfigError(ValueError):
    ...


def get_instance_path():
    instance_path = os.environ.get("FLOW_INSTANCE_PATH")
    if not instance_path:
        raise click.UsageError(
            'You did not provide the "FLOW_INSTANCE_PATH" environment variable.'
        )
    elif os.path.exists(instance_path) and os.path.isabs(instance_path):
        return instance_path
    else:
        raise click.UsageError(
            'Incorrect path set in "FLOW_INSTANCE_PATH" environment variable.'
        )


def get_config():
    if not os.path.exists(instance_path):
        os.mkdir(instance_path)

    fpath = os.path.join(instance_path, "config.json")

    if not os.path.exists(fpath):
        with open(os.path.join(cur_path, "sample_config.json")) as f:
            sample_config = f.read()
        with open(fpath, "a+") as f:
            f.write(sample_config)

    with open(fpath) as f:
        conf_dict = json.load(f)
        return Conf(**conf_dict)


def config_required(f: Callable[..., Any]) -> Callable[..., Any]:
    def decorator(*args: Any, **kwargs: Any):
        validate_config()
        f(*args, **kwargs)

    return decorator


def validate_config():
    for k, v in conf.__dict__.items():
        if not k or not v:
            raise WrongConfigError("Configuration is not complete")


def get_channel(name: str):
    for d in conf.channels:
        if d["name"] == name:
            return d
    raise ValueError(f'No such channel: "{name}"')


cur_path = pathlib.Path(__file__).parent
instance_path = get_instance_path()
conf = get_config()
