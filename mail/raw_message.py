import base64
import binascii
import re


MAX_RAW_MESSAGE_BYTES = 25 * 1024 * 1024
BASE64URL_RE = re.compile(b"^[A-Za-z0-9_-]*={0,2}$")

try:
    TEXT_TYPE = unicode
    BYTE_TYPE = str
    INTEGER_TYPES = (int, long)
except NameError:
    TEXT_TYPE = str
    BYTE_TYPE = bytes
    INTEGER_TYPES = (int,)


def decode_raw_message(raw_value, max_bytes=MAX_RAW_MESSAGE_BYTES):
    if isinstance(max_bytes, bool) or not isinstance(max_bytes, INTEGER_TYPES) or max_bytes <= 0:
        raise ValueError("Raw message limit must be a positive integer.")
    if not isinstance(raw_value, (TEXT_TYPE, BYTE_TYPE)) or not raw_value:
        raise ValueError("Raw Gmail message must be a non-empty string.")

    if isinstance(raw_value, TEXT_TYPE):
        try:
            encoded = raw_value.encode("ascii")
        except UnicodeEncodeError:
            raise ValueError("Raw Gmail message must be ASCII base64url.")
    else:
        encoded = raw_value

    if not BASE64URL_RE.match(encoded):
        raise ValueError("Raw Gmail message must use the base64url alphabet.")
    if b"=" in encoded and len(encoded) % 4 != 0:
        raise ValueError("Raw Gmail message has invalid padding.")
    if len(encoded) % 4 == 1:
        raise ValueError("Raw Gmail message has an invalid encoded length.")

    max_encoded_length = ((max_bytes + 2) // 3) * 4
    if len(encoded) > max_encoded_length:
        raise ValueError("Raw Gmail message exceeds the encoded size limit.")

    padded = encoded + (b"=" * ((4 - len(encoded) % 4) % 4))
    try:
        decoded = base64.urlsafe_b64decode(padded)
    except (TypeError, binascii.Error):
        raise ValueError("Raw Gmail message is not valid base64url.")
    if len(decoded) > max_bytes:
        raise ValueError("Raw Gmail message exceeds the decoded size limit.")
    return decoded
