DROP TABLE IF EXISTS post;
CREATE TABLE post (
    channel_name TEXT NOT NULL,
    is_published INT NOT NULL DEFAULT 0 CHECK (is_published IN (0, 1)),
    date_added TIMESTAMP NOT NULL DEFAULT (datetime('now', 'localtime')),
    content TEXT,
    photos TEXT,
    vk_post_id INT NOT NULL PRIMARY KEY,
    vk_post_date TIMESTAMP NOT NULL,
    vk_group_id INT NOT NULL,
    tg_post_ids TEXT,
    tg_post_date TIMESTAMP,
    tg_chat_id INT
);