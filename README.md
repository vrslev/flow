# Flow

Simple command line tool for reposting from VK Group to Telegram channel. Uses official APIs.

## Installing

1. Install this package:

```zsh
pip install https://github.com/vrslev/flow.git
```

2. Create `instance` directory where database, config and log will live.
3. Export absolute path to this directory to `FLOW_INSTANCE_PATH` in your shell, for example:

```zsh
export FLOW_INSTANCE_PATH=/Users/lev/flow
```

In future, add this in your `.bashprofile` or `.zshrc`.

4. Next, run `flow init-db` to initialize database and config file.
5. [Create a VK App](https://vk.com/apps?act=manage).
6. Go to `config.json` in directory you created and fill `vk_app_id` and `vk_app_service_token`.
7. [Create Telegram bot](https://t.me/BotFather).
8. Fill `tg_bot_username` and `tg_bot_token` in `config.json`.
9. Run `flow add-channel` and follow instructions in order to add new channel.

Installation is complete!

## Usage

`flow fetch` gets new posts from source VK group.

`flow publish` sends fetched posts in target Telegram channel. You can limit of posts with `--limit` option.

`flow run` executes `flow fetch` and then `flow publish` every 1 minute.
