import re
from typing import Optional

from emoji import unicode_codes


def format_text(text: Optional[str]):
    if not text:
        return

    text = remove_multiple_line_breakers(text)
    text = fix_quotes(text)
    text = fix_dash(text)
    text = remove_multiple_punctuation_marks(text)
    text = fix_spaces_near_punctuation_marks(text)
    text = make_header(text)
    text = remove_multiple_line_breakers(text)
    text = format_internal_vk_links(text)
    text = remove_multiple_spaces(text)
    text = remove_space_in_new_line(text)
    text = remove_spaces_in_start_and_end(text)
    return text


def remove_multiple_line_breakers(text: str):
    return re.sub(r"(\n\n)[\n]+", r"\g<1>", text)


def remove_space_in_new_line(text: str):
    return text.replace("\n ", "\n")


def remove_multiple_spaces(text: str):
    return re.sub(r" +", " ", text)


def remove_multiple_punctuation_marks(text: str):
    text = re.sub(r"(\.\.\.)[\.]+", r"\g<1>", text)
    text = re.sub(r"!+", "!", text)
    text = re.sub(r"\?+", "?", text)
    return text


def fix_quotes(text: str):
    return re.sub(r"\"([^\"]+)\"", r"«\g<1>»", text)


def fix_dash(text: str):
    return re.sub(r"( - )|( – )", " — ", text)


def fix_spaces_near_punctuation_marks(text: str):
    text = re.sub(r" ?([\)\.!\?]+) ?", r"\g<1> ", text)
    text = re.sub(r" ?([\(]) ?", r" (", text)
    return text


def get_emoji_regexp():
    # Taken from `emoji`. Their version compiles pattern, this does not
    emojis = sorted(unicode_codes.EMOJI_UNICODE["en"].values(), key=len, reverse=True)
    pattern = "(" + "|".join(re.escape(u) for u in emojis) + ")"
    return pattern


def make_header(text: str):
    if "\n" not in text:
        return text

    symbols = r"\.\.\.|[\n\.!\?]|[%s]+" % get_emoji_regexp()
    regex = re.compile(
        r"(^[\w ,]+(%s))" % symbols,
        flags=re.UNICODE,
    )
    new_text = re.sub(regex, r"*\g<1>*\n\n", text)

    new_text = new_text.replace("\n*", "*")
    if new_text == text:
        new_text = re.sub(rf"(^[^\w]+[^\n]+?[^\w]+?)\n", r"\g<1>\n", text)

    return new_text


def remove_spaces_in_start_and_end(text: str):
    return re.sub(r"^\s+|\s+$", "", text)


def format_internal_vk_links(text: str):
    regex = re.compile(r"\[([^\|\]]+)\|([^\]]+)\]")
    match = regex.findall(text)
    if len(match) > 0:
        for user_id, username in match:
            text = text.replace(
                f"[{user_id}|{username}]",
                f"[{username}](https://vk.com/{user_id})",
            )
    return text


__all__ = ["format_text"]
