import logging
import os

from .config import instance_path
from .database import db_path, init_db

__version__ = "0.0.1"

__description__ = "CLI for reposting from VK to Telegram"
__url__ = "https://github.com/vrslev/flow"

__author__ = "Lev Vereshchagin"
__email__ = "mail@vrslev.com"

__license__ = "MIT"


if not os.path.exists(db_path):
    init_db()

logging.basicConfig(
    filename=os.path.join(instance_path, "flow.log"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
)
