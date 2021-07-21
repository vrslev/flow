import re
from typing import Optional

emoji = "\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF"  # TODO: Not working


def format_text(text: Optional[str]):
    if not text:
        return

    text = remove_multiple_line_breakers(text)
    text = remove_space_in_new_line(text)
    text = remove_multiple_spaces(text)
    text = remove_multiple_punctuation_marks(text)
    text = fix_quotes(text)
    text = fix_dash(text)
    text = fix_spaces_near_punctuation_marks(text)
    text = make_header(text)
    text = remove_multiple_line_breakers(text)
    text = format_internal_vk_links(text)
    text = remove_spaces_in_start_and_end(text)
    return text


def remove_multiple_line_breakers(text: str):
    if len([d for d in re.split(r"\n+\s?", text) if d]) < 3:
        return re.sub(r"\n+", "\n", text)
    else:
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


def make_header(text: str):
    if "\n" not in text:
        return text
    symbols = rf"\.\.\.|[\n\.!\?]|[{emoji}]+"
    regex = re.compile(
        rf"(^[\w ,]+({symbols}))",
        flags=re.UNICODE,
    )
    new_text = re.sub(regex, r"<b>\g<1></b>\n\n", text)
    new_text = new_text.replace("\n</b>", "</b>")
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
                f'<a href="https://vk.com/{user_id}">{username}</a>',
            )
    return text


__all__ = ["format_text"]
