# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXT_PAYLOAD_PATH = os.path.join(ROOT, "mail", "text_payload.py")
try:
    from importlib import util as importlib_util
except ImportError:
    import imp

    TEXT_PAYLOAD = imp.load_source("text_payload", TEXT_PAYLOAD_PATH)
else:
    SPEC = importlib_util.spec_from_file_location("text_payload", TEXT_PAYLOAD_PATH)
    TEXT_PAYLOAD = importlib_util.module_from_spec(SPEC)
    SPEC.loader.exec_module(TEXT_PAYLOAD)


class FakePart(object):
    def __init__(self, decoded_payload, charset=None, raw_payload=None):
        self.decoded_payload = decoded_payload
        self.charset = charset
        self.raw_payload = raw_payload

    def get_payload(self, decode=False):
        if decode:
            return self.decoded_payload
        return self.raw_payload

    def get_content_charset(self):
        return self.charset


class TextPayloadTests(unittest.TestCase):
    def test_uses_valid_declared_charset(self):
        part = FakePart(b"caf\xe9", charset="iso-8859-1")

        self.assertEqual(TEXT_PAYLOAD.decode_text_payload(part), "café")

    def test_missing_charset_uses_utf8_replacement(self):
        part = FakePart(b"hello \xff")

        self.assertEqual(TEXT_PAYLOAD.decode_text_payload(part), "hello \ufffd")

    def test_unknown_charset_uses_utf8_replacement(self):
        part = FakePart(b"hello \xff", charset="x-unknown")

        self.assertEqual(TEXT_PAYLOAD.decode_text_payload(part), "hello \ufffd")

    def test_malformed_declared_charset_bytes_are_replaced(self):
        part = FakePart(b"hello \xff", charset="utf-8")

        self.assertEqual(TEXT_PAYLOAD.decode_text_payload(part), "hello \ufffd")

    def test_string_payload_is_preserved(self):
        part = FakePart(None, raw_payload="already decoded")

        self.assertEqual(TEXT_PAYLOAD.decode_text_payload(part), "already decoded")

    def test_absent_payload_becomes_empty_text(self):
        part = FakePart(None)

        self.assertEqual(TEXT_PAYLOAD.decode_text_payload(part), "")

    def test_decoded_payload_is_bounded_before_text_parsing(self):
        part = FakePart(b"0123456789", charset="ascii")

        self.assertEqual(
            TEXT_PAYLOAD.decode_text_payload(part, max_bytes=4),
            "0123",
        )

    def test_unicode_payload_is_bounded_without_splitting_code_points(self):
        part = FakePart(None, raw_payload="café012345")

        self.assertEqual(
            TEXT_PAYLOAD.decode_text_payload(part, max_bytes=4),
            "caf",
        )


if __name__ == "__main__":
    unittest.main()
