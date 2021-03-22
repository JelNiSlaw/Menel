import re


def mention(user_id: int) -> re.Pattern:
    return re.compile(rf'<@!?{user_id}>')


USER_MENTION = re.compile(r'<@!?(?P<ID>\d{15,20})>')
DISCORD_ID = re.compile(r'\d{15,20}')
CODEBLOCK = re.compile(r'```(?P<language>\w*)\s*(?P<code>.*)\s*```', re.DOTALL)