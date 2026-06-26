#!/usr/bin/env python3
import pathlib
import sys


helper = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
integration = pathlib.Path(sys.argv[2]).read_text(encoding="utf-8")

for contract in (
    "MAX_RAW_MESSAGE_BYTES = 25 * 1024 * 1024",
    'BASE64URL_ALPHABET = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"',
    'BASE64URL_RE = re.compile(b"^[A-Za-z0-9_-]*={0,2}$")',
    "def gmail_raw_value(response):",
    "if not isinstance(response, dict):",
    'return response.get("raw")',
    "def decode_raw_message(raw_value, max_bytes=MAX_RAW_MESSAGE_BYTES):",
    "if not isinstance(raw_value, (TEXT_TYPE, BYTE_TYPE)) or not raw_value:",
    "if not BASE64URL_RE.match(encoded):",
    'if b"=" in encoded and len(encoded) % 4 != 0:',
    "max_encoded_length = ((max_bytes + 2) // 3) * 4",
    "if len(encoded) > max_encoded_length:",
    'unpadded = encoded.rstrip(b"=")',
    "pad_bit_mask = {2: 0x0F, 3: 0x03}.get(len(unpadded) % 4, 0)",
    "last_value = BASE64URL_ALPHABET.find(unpadded[-1:])",
    "if pad_bit_mask and (last_value & pad_bit_mask):",
    'raise ValueError("Raw Gmail message is not canonical base64url.")',
    "decoded = base64.urlsafe_b64decode(padded)",
    "if len(decoded) > max_bytes:",
):
    if helper.count(contract) != 1:
        raise SystemExit(f"Raw message helper must contain one {contract!r}.")

tests = pathlib.Path(sys.argv[3]).read_text(encoding="utf-8")
for contract in (
    "test_accepts_canonical_one_and_two_byte_final_quanta",
    'b"AQ=="',
    'b"AQ"',
    'b"AQI="',
    'b"AQI"',
    "test_rejects_noncanonical_discarded_pad_bits",
    'b"AR=="',
    'b"AR"',
    'b"AQJ="',
    'b"AQJ"',
):
    if tests.count(contract) != 1:
        raise SystemExit(f"Raw message tests must contain one {contract!r}.")

if not helper.index("pad_bit_mask =") < helper.index("base64.urlsafe_b64decode(padded)"):
    raise SystemExit("Canonical pad bits must be checked before decoded-body allocation.")

handler = integration.split("def GetMimeMessage", 1)[1].split("class Single", 1)[0]
contracts = (
    "message = service.users().messages().get",
    "msg_str = decode_raw_message(gmail_raw_value(message))",
    "except ValueError:",
    "msg = parse_raw_mime(msg_str)",
    "if msg is None:",
)
for contract in contracts:
    if handler.count(contract) != 1:
        raise SystemExit(f"GetMimeMessage must contain one {contract!r}.")
if not all(handler.index(a) < handler.index(b) for a, b in zip(contracts, contracts[1:])):
    raise SystemExit("GetMimeMessage must contain invalid raw data before MIME parsing.")
raw_failure = handler.index("except ValueError:")
parser_call = handler.index("msg = parse_raw_mime(msg_str)")
if handler.find("return None", raw_failure, parser_call) == -1:
    raise SystemExit("Invalid raw Gmail data must fail closed before MIME parsing.")

print("Raw Gmail MIME boundary checks passed.")
