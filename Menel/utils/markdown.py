from typing import Any


def bold(text: Any) -> str:
    return f'**{text}**'


def italic(text: Any) -> str:
    return f'*{text}*'


def underlined(text: Any) -> str:
    return f'__{text}__'


def strikethrough(text: Any) -> str:
    return f'~~{text}~~'


def spoiler(text: Any) -> str:
    return f'||{text}||'


def code(text: Any) -> str:
    return f'`{text}`'


def codeblock(text: str, language: str = '', escape: bool = True) -> str:
    if escape:
        zwsp = '\N{ZERO WIDTH SPACE}'
        text = text.replace('```', f'`{zwsp}`{zwsp}`')
    return f'```{language}\n{text}\n```'