import re


def mention(user_id: int) -> re.Pattern:
    return re.compile(rf'<@!?{user_id}>', re.IGNORECASE | re.ASCII)


USER_MENTION = re.compile(r'<@!?(?P<ID>\d{18})>', re.IGNORECASE)