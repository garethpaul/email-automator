# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
import os
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_MESSAGE_PATH = os.path.join(ROOT, "mail", "raw_message.py")
try:
    from importlib import util as importlib_util
except ImportError:
    import imp

    RAW_MESSAGE = imp.load_source("raw_message", RAW_MESSAGE_PATH)
else:
    SPEC = importlib_util.spec_from_file_location("raw_message", RAW_MESSAGE_PATH)
    RAW_MESSAGE = importlib_util.module_from_spec(SPEC)
    SPEC.loader.exec_module(RAW_MESSAGE)


class RawMessageTests(unittest.TestCase):
    def test_gmail_raw_value_rejects_malformed_response_shapes(self):
        for response in (None, [], "raw", 123):
            self.assertIsNone(RAW_MESSAGE.gmail_raw_value(response))

    def test_gmail_raw_value_returns_mapping_raw_field_unchanged(self):
        raw = b"U3ViamVjdDogaGVsbG8NCg0KYm9keQ"

        self.assertEqual(raw, RAW_MESSAGE.gmail_raw_value({"raw": raw}))
        self.assertIsNone(RAW_MESSAGE.gmail_raw_value({}))

    def test_decodes_padded_and_unpadded_base64url(self):
        payload = b"Subject: hello\r\n\r\nbody"
        encoded = base64.urlsafe_b64encode(payload)

        self.assertEqual(payload, RAW_MESSAGE.decode_raw_message(encoded))
        self.assertEqual(payload, RAW_MESSAGE.decode_raw_message(encoded.rstrip(b"=")))

    def test_accepts_canonical_one_and_two_byte_final_quanta(self):
        for raw, expected in (
            (b"AQ==", b"\x01"),
            (b"AQ", b"\x01"),
            (b"AQI=", b"\x01\x02"),
            (b"AQI", b"\x01\x02"),
        ):
            self.assertEqual(expected, RAW_MESSAGE.decode_raw_message(raw))

    def test_rejects_absent_non_string_and_non_ascii_values(self):
        for raw in (None, b"", 123, [], "caf\u00e9"):
            with self.assertRaises(ValueError):
                RAW_MESSAGE.decode_raw_message(raw)

    def test_rejects_invalid_alphabet_whitespace_and_padding(self):
        for raw in (b"a!bc", b"ab c", b"ab\nc", b"a===", b"ab=c", b"a"):
            with self.assertRaises(ValueError):
                RAW_MESSAGE.decode_raw_message(raw)

    def test_rejects_noncanonical_discarded_pad_bits(self):
        for raw in (b"AR==", b"AR", b"AQJ=", b"AQJ"):
            with self.assertRaises(ValueError):
                RAW_MESSAGE.decode_raw_message(raw)

    def test_rejects_encoded_values_above_preflight_limit(self):
        with self.assertRaises(ValueError):
            RAW_MESSAGE.decode_raw_message(b"QUJDRA==", max_bytes=3)

    def test_rejects_decoded_values_above_limit(self):
        encoded = base64.urlsafe_b64encode(b"ABCDE").rstrip(b"=")

        with self.assertRaises(ValueError):
            RAW_MESSAGE.decode_raw_message(encoded, max_bytes=4)


if __name__ == "__main__":
    unittest.main()
