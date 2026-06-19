import base64
from email.mime.text import MIMEText

try:
    TEXT_TYPE = unicode
    BYTE_TYPE = str
except NameError:
    TEXT_TYPE = str
    BYTE_TYPE = bytes


def encode_raw_message(raw_message):
    if isinstance(raw_message, TEXT_TYPE):
        raw_message = raw_message.encode("utf-8")
    if not isinstance(raw_message, BYTE_TYPE):
        raise TypeError("Raw reply message must be text or bytes.")
    return base64.urlsafe_b64encode(raw_message).decode("ascii")


def _safe_header(value):
    if not isinstance(value, (TEXT_TYPE, BYTE_TYPE)):
        raise ValueError("Reply headers must be strings.")
    if "\r" in value or "\n" in value or "\x00" in value:
        raise ValueError("Reply headers must not contain control line breaks.")
    return value


def create_message(sender, recipient, subject, message_text):
    sender = _safe_header(sender)
    recipient = _safe_header(recipient)
    subject = _safe_header(subject)
    try:
        message = MIMEText(message_text)
    except UnicodeEncodeError:
        message = MIMEText(message_text, _charset="utf-8")
    message["To"] = recipient
    message["From"] = sender
    message["Subject"] = subject
    return {"raw": encode_raw_message(message.as_string())}
