try:
    TEXT_TYPE = unicode
    INTEGER_TYPES = (int, long)
except NameError:
    TEXT_TYPE = str
    INTEGER_TYPES = (int,)

MAX_TEXT_PAYLOAD_BYTES = 1024 * 1024


def _bounded_unicode(value, max_bytes):
    encoded = value.encode("utf-8")
    if len(encoded) <= max_bytes:
        return value
    return encoded[:max_bytes].decode("utf-8", errors="ignore")


def decode_text_payload(part, max_bytes=MAX_TEXT_PAYLOAD_BYTES):
    if isinstance(max_bytes, bool) or not isinstance(max_bytes, INTEGER_TYPES) or max_bytes <= 0:
        raise ValueError("Text payload limit must be a positive integer.")
    payload = part.get_payload(decode=True)
    if payload is None:
        payload = part.get_payload()
    if payload is None:
        return u""
    if isinstance(payload, TEXT_TYPE):
        return _bounded_unicode(payload, max_bytes)

    payload = payload[:max_bytes]

    charset = part.get_content_charset() or "utf-8"
    try:
        return payload.decode(charset, errors="replace")
    except (LookupError, TypeError):
        return payload.decode("utf-8", errors="replace")
