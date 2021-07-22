# Flow

Простая утилита командная строки для репоста постов из группы VK в канал Telegram

[English](https://github.com/vrslev/flow/blob/main/README.md)

## Настройка

1. Убедитесь, что на борту Python 3.9.
2. Если хотите, создайте виртульную среду Python:

```zsh
mkdir flow
cd flow
python3 -m venv venv
source venv/bin/activate
```

3. Установите пакет

```zsh
pip install git+https://github.com/vrslev/flow.git
```

4. Создайте папку `instance`, где будут жить база данных, конфиг и лог.
5. Экспортируйте абсолютный путь к этой папке в переменную окружения, например:

```zsh
export FLOW_INSTANCE_PATH=/home/lev/flow/instance
```

В будущем, это можно добавить в ваш `.bashprofile` или `.zshrc`.

6. Выполните команду `flow` в терминале, чтобы инициализировать базу данных, конфиг и лог.
7. [Создайте приложение VK](https://vk.com/apps?act=manage).
8. Откройте `config.json` в папке, которую вы создали и заполните `vk_app_id` (ID приложения) и `vk_app_service_token` (сервисный токен приложения).
9. [Создайте Telegram-бота](https://t.me/BotFather).
10. Заполните `tg_bot_username` (имя бота) and `tg_bot_token` (токен бота) в `config.json`.
11. Выполните `flow add-channel` в терминале и продолжите в соответствии с данными инструкциями, чтобы добавить канал.

Установка завершена!

## Использование

`flow fetch` получает новые посты из группы VK.

`flow publish` посылает полученные посты в канал Telegram. Вы можете ограничить количество постов с опцией `--limit` и установить интервал между постами с помощью `--post-frequency`.

`flow run` исполняет `flow fetch` и затем `flow publish` периодически. Используйте опцию `--fetch-interval`, чтобы установить, как часто это будет происходить и `--post-frequency` чтобы установить частоту постов.
