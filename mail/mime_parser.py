from email import message_from_string

try:
    from email import message_from_bytes
except ImportError:
    message_from_bytes = None

try:
    TEXT_TYPE = unicode
    BYTE_TYPE = str
except NameError:
    TEXT_TYPE = str
    BYTE_TYPE = bytes


def parse_raw_mime(raw_message):
    if not isinstance(raw_message, (TEXT_TYPE, BYTE_TYPE)):
        return None
    try:
        if message_from_bytes is not None and isinstance(raw_message, BYTE_TYPE):
            return message_from_bytes(raw_message)
        return message_from_string(raw_message)
    except (TypeError, ValueError, RuntimeError):
        return None
