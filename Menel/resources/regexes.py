import re


def mention(user_id: int) -> re.Pattern:
    return re.compile(rf'<@!?{user_id}>')


USER_MENTION = re.compile(r'<@!?(?P<ID>\d{18})>')
DISCORD_ID = re.compile(r'\d{18}')