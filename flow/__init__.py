import logging
import os

from .config import get_instance_path

__version__ = "0.0.2"

__description__ = "CLI for reposting from VK to Telegram"
__url__ = "https://github.com/vrslev/flow"

__author__ = "Lev Vereshchagin"
__email__ = "mail@vrslev.com"

__license__ = "MIT"


logging.basicConfig(
    filename=os.path.join(get_instance_path(), "flow.log"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
)
