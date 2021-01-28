def constant_length_text(text: str, length: int):
    if len(text) > length:
        return text[:length - 1] + '…'
    else:
        return text.ljust(length, ' ')