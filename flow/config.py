import json
import os
import pathlib
from typing import Any, Callable

from .types import Conf


class WrongConfigError(ValueError):
    ...


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


cur_path = pathlib.Path(__file__).parent
instance_path = os.path.join(cur_path.parent, "instance")
conf = get_config()


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
