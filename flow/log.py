import logging
import os
from typing import Any, Optional

# TODO: Relocate all things related to cli to `cli.py`
import click

from .config import instance_path
from .database import db

logging.basicConfig(
    filename=os.path.join(instance_path, "news.log"),
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


def patch_echo():
    old_echo = click.echo  # type: ignore

    def custom_click_echo(
        message: Optional[str], *args: Optional[Any], **kwargs: Optional[Any]
    ):
        logger.info(message)
        return old_echo(message=message, *args, **kwargs)

    click.echo = custom_click_echo


patch_echo()


class CustomClickGroup(click.Group):
    """Custom click.Group class to enable logging all exceptions"""

    def __call__(self, *args: Optional[Any], **kwargs: Optional[Any]) -> Optional[Any]:
        try:
            return self.main(*args, **kwargs)  # type: ignore
        except Exception as e:
            logger.error(e, exc_info=True)
            db.close()
            raise e
