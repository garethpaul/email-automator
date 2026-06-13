try:
    TEXT_TYPE = unicode
except NameError:
    TEXT_TYPE = str


def decode_text_payload(part):
    payload = part.get_payload(decode=True)
    if payload is None:
        payload = part.get_payload()
    if payload is None:
        return u""
    if isinstance(payload, TEXT_TYPE):
        return payload

    charset = part.get_content_charset() or "utf-8"
    try:
        return payload.decode(charset, errors="replace")
    except (LookupError, TypeError):
        return payload.decode("utf-8", errors="replace")
