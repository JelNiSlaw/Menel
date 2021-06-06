def bold(text: str) -> str:
    return f'**{text}**'


def italic(text: str) -> str:
    return f'*{text}*'


def underlined(text: str) -> str:
    return f'__{text}__'


def strikethrough(text: str) -> str:
    return f'~~{text}~~'


def code(text: str) -> str:
    return f'`{text}`'


def codeblock(text: str, language: str = '', escape: bool = True) -> str:
    return f'```{language}\n{text.replace("`", "​`") if escape else text}\n```'


def spoiler(text: str) -> str:
    return f'||{text}||'