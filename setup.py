import os
import re

from setuptools import find_packages, setup

NAME = "flow"

KEYWORDS = ["vk", "vkontakte", "telegram", "telegram bot", "tg", "tg bot"]
CLASSIFIERS = [
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
]

PYTHON_REQUIRES = ">=3.9"
INSTALL_REQUIRES = [
    "python-telegram-bot~=13.7",
    "click~=8.0",
    "schedule",
    "emoji~=1.4.1",
    "pyyaml",
]
EXTRAS_REQUIRE = {"dev": ["pre-commit", "black"], "sentry": ["sentry_sdk"]}

PACKAGES = find_packages()

HERE = os.path.abspath(os.path.dirname(__file__))
LONG_DESCRIPTION = open(os.path.join(HERE, "README.md")).read()
META_FILE = open(os.path.join(HERE, "flow", "__init__.py")).read()


def find_meta(meta: str):
    """
    Extract __*meta*__ from META_FILE.
    Taken from structlog (https://github.com/hynek/structlog/blob/main/setup.py)
    """
    meta_match = re.search(fr"^__{meta}__ = ['\"]([^'\"]*)['\"]", META_FILE, re.M)
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError(f"Unable to find __{ meta }__ string.")


if __name__ == "__main__":
    setup(
        name=NAME,
        description=find_meta("description"),
        license=find_meta("license"),
        url=find_meta("url"),
        version=find_meta("version"),
        author=find_meta("author"),
        author_email=find_meta("email"),
        maintainer=find_meta("author"),
        maintainer_email=find_meta("email"),
        long_description=LONG_DESCRIPTION,
        long_description_content_type="text/markdown",
        keywords=KEYWORDS,
        packages=PACKAGES,
        classifiers=CLASSIFIERS,
        python_requires=PYTHON_REQUIRES,
        install_requires=INSTALL_REQUIRES,
        extras_require=EXTRAS_REQUIRE,
        include_package_data=True,
        zip_safe=False,
        entry_points={"console_scripts": ["flow = flow.cli:cli"]},
    )
