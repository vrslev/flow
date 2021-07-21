# TODO: Write readme
# TODO: In config, change telegram to tg
__version__ = "0.0.1"

import logging
import os

from .config import instance_path

logging.basicConfig(
    filename=os.path.join(instance_path, "flow.log"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
)
