#!/usr/bin/env python3
import pathlib
import sys


helper = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
integration = pathlib.Path(sys.argv[2]).read_text(encoding="utf-8")

for contract in (
    "MAX_RAW_MESSAGE_BYTES = 25 * 1024 * 1024",
    'BASE64URL_RE = re.compile(b"^[A-Za-z0-9_-]*={0,2}$")',
    "def decode_raw_message(raw_value, max_bytes=MAX_RAW_MESSAGE_BYTES):",
    "if not isinstance(raw_value, (TEXT_TYPE, BYTE_TYPE)) or not raw_value:",
    "if not BASE64URL_RE.match(encoded):",
    'if b"=" in encoded and len(encoded) % 4 != 0:',
    "max_encoded_length = ((max_bytes + 2) // 3) * 4",
    "if len(encoded) > max_encoded_length:",
    "decoded = base64.urlsafe_b64decode(padded)",
    "if len(decoded) > max_bytes:",
):
    if helper.count(contract) != 1:
        raise SystemExit(f"Raw message helper must contain one {contract!r}.")

handler = integration.split("def GetMimeMessage", 1)[1].split("class Single", 1)[0]
contracts = (
    "message = service.users().messages().get",
    "msg_str = decode_raw_message(message.get('raw'))",
    "except ValueError:",
    "return None",
    "msg = message_from_string(msg_str)",
)
for contract in contracts:
    if handler.count(contract) != 1:
        raise SystemExit(f"GetMimeMessage must contain one {contract!r}.")
if not all(handler.index(a) < handler.index(b) for a, b in zip(contracts, contracts[1:])):
    raise SystemExit("GetMimeMessage must contain invalid raw data before MIME parsing.")

print("Raw Gmail MIME boundary checks passed.")
