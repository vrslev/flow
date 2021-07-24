import logging
import os

from . import config

__version__ = "0.0.3"

__description__ = "CLI for reposting from VK to Telegram"
__url__ = "https://github.com/vrslev/flow"

__author__ = "Lev Vereshchagin"
__email__ = "mail@vrslev.com"

__license__ = "MIT"


logging.basicConfig(
    filename=os.path.join(config.get_instance_path(), "flow.log"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
)

if _sentry_dsn := os.environ.get("SENTRY_DSN"):
    # pyright: reportMissingImports=false, reportUnknownVariableType=false
    import sentry_sdk as _sentry_sdk
    from sentry_sdk.integrations.logging import (
        LoggingIntegration as _LoggingIntegration,
    )

    sentry_logging = _LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)
    _sentry_sdk.init(dsn=_sentry_dsn, integrations=[sentry_logging])
