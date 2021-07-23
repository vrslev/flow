from dataclasses import dataclass

from telegram.files.inputmedia import InputMediaPhoto
from telegram.message import Message

from .api.telegram import CustomBot
from .format import format_text
from .storage import Post


@dataclass
class Chat:
    bot: CustomBot
    chat_id: int
    format_text: bool

    def publish_post(self, post: Post):
        content = post.content
        if self.format_text:
            content = format_text(content)

        sent_messages: list[Message] = []

        if not post.photos and post.content:
            sent_messages = self.bot.send_message(chat_id=self.chat_id, text=content)
        elif post.photos:
            if len(post.photos) == 1:
                sent_messages = self.bot.send_photo(
                    chat_id=self.chat_id, photo=post.photos[0], caption=content
                )
            else:
                sent_messages = self.bot.send_media_group(
                    chat_id=self.chat_id,
                    media=[InputMediaPhoto(media=p) for p in post.photos],
                    disable_notification=True,  # prevent double notification
                    text=content,
                    timeout=60,
                )
        return sent_messages
