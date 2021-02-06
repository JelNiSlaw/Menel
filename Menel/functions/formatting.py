def bold(text: str) -> str:
    return f'**{text}**'


def italic(text: str) -> str:
    return f'*{text}*'


def underlined(text: str) -> str:
    return f'__{text}__'


def strikethrough(text: str) -> str:
    return f'~~{text}~~'


def code(text: str, escape: bool = True) -> str:
    return f'`{_escape_code(text) if escape else text}`'


def codeblock(text: str, language: str = '', escape: bool = True) -> str:
    return f'```{language}\n{_escape_code(text) if escape else text}\n```'


def spoiler(text: str) -> str:
    return f'||{text}||'


def _escape_code(text: str) -> str:
    return text.replace('`', '​`')