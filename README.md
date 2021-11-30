# vrslev/flow

Simple app for reposting posts from VK to Telegram. Can be easily deployed as AWS lambda function.

## Configuration

Since main deployment method is as lambda function, configuration is done with environment variables.

### `VK_TOKEN`

VK app service token. To get it you need to [create a VK app](https://vk.com/apps?act=manage) and copy app service token from there.

### `VK_OWNER_ID`

<!-- TODO: Continue after simple cli to get it is done -->

### `TG_TOKEN`

Telegram bot token. [Create a bot](https://t.me/BotFather)

### `TG_CHAT_ID`

Target Telegram chat or channel id.

<!-- TODO: Continue after simple cli for this too is done -->

### `DB_PATH`

Path to SQLite database file. Default is `/tmp/database.db`

### `SENTRY_DSN` (optional)

DSN for sentry error reports

## Usage

### Lambda

1. Set up S3 bucket,
2. Set these environment variables along with variables in [Configuration section](#configuration): `S3_BUCKET`, `S3_KEY`, `S3_ENDPOINT`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`,
3. Set entrypoint to `flow.main.lambda_handler`,
4. Clone this repo and upload zip archive generated by `bash scripts/prepare_artifact.sh`,
5. Configure timer trigger for the function.

### Local setup

1. Clone and install the app. Note that you need to have poetry installed.

```console
git clone --depth 1 https://github.com/vrslev/flow.git
cd flow
poetry install
```

2. Configure .env file with [the variables](#configuration),
3. Run:

```console
poetry run python3 flow/main.py
```

### With Python as library

1. Install with pip:

```console
pip install git+https://github.com/vrslev/flow.git
```

2. Use `flow` wherever you want. For example:

```python
from flow.main import main
from flow.models import Settings

settings = Settings()
main(settings)

```

Each call publishes only one post, doesn't matter if there's more available. This is done so you can easily customize publishing schedule (and use it in lambda 😏).
