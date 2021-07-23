# Flow

Simple command line tool for reposting from VK Group to Telegram channel. Uses official APIs.

[Русский](https://github.com/vrslev/flow/blob/main/README_RU.md)

## Setup

1. Make sure you have Python 3.9 onboard.
2. Create virtualenv if you want:

```zsh
mkdir flow
cd flow
python3 -m venv venv
source venv/bin/activate
```

3. Install this package:

```zsh
pip install git+https://github.com/vrslev/flow.git
```

4. Create `instance` directory where database, config and log will live.
5. Export absolute path to this directory to `FLOW_INSTANCE_PATH` in your shell, for example:

```zsh
export FLOW_INSTANCE_PATH=/home/lev/flow/instance
```

In future, add this in your `.bashprofile` or `.zshrc`.

6. Run `flow` to initialize database, config and log files.
7. [Create a VK App](https://vk.com/apps?act=manage).
8. Open `config.yaml` in directory you created and fill `vk_app_id` and `vk_app_service_token`.
9. [Create Telegram bot](https://t.me/BotFather).
10. Fill `tg_bot_username` and `tg_bot_token` in `config.yaml`.
11. Run `flow add-channel` and follow instructions in order to add new channel.

Installation is complete!

## Usage

`flow fetch` gets new posts from source VK group.

`flow publish` sends fetched posts in target Telegram channel. You can limit number posts with `--limit` option and set interval between posts with `--post-frequency`.

`flow run` executes `flow fetch` and then `flow publish` periodically. Use `--fetch-interval` to set how often this will happen and `--post-frequency` to set interval between posts.
