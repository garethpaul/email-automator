# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIME_PARSER_PATH = os.path.join(ROOT, "mail", "mime_parser.py")
try:
    from importlib import util as importlib_util
except ImportError:
    import imp

    MIME_PARSER = imp.load_source("mime_parser", MIME_PARSER_PATH)
else:
    SPEC = importlib_util.spec_from_file_location("mime_parser", MIME_PARSER_PATH)
    MIME_PARSER = importlib_util.module_from_spec(SPEC)
    SPEC.loader.exec_module(MIME_PARSER)


def nested_message(depth):
    chunks = []
    for index in range(depth):
        boundary = ("level-%d" % index).encode("ascii")
        chunks.append(
            b'Content-Type: multipart/mixed; boundary="'
            + boundary
            + b'"\r\n\r\n--'
            + boundary
            + b"\r\n"
        )
    chunks.append(b"Content-Type: text/plain\r\n\r\nbody\r\n")
    for index in reversed(range(depth)):
        boundary = ("level-%d" % index).encode("ascii")
        chunks.append(b"--" + boundary + b"--\r\n")
    return b"".join(chunks)


class MimeParserTests(unittest.TestCase):
    def test_parses_valid_raw_message_bytes(self):
        message = MIME_PARSER.parse_raw_mime(b"Subject: hello\r\n\r\nbody")

        self.assertIsNotNone(message)
        self.assertEqual(message.get("Subject"), "hello")

    def test_recursion_exhaustion_fails_closed(self):
        self.assertIsNone(MIME_PARSER.parse_raw_mime(nested_message(1100)))

    def test_non_string_input_fails_closed(self):
        self.assertIsNone(MIME_PARSER.parse_raw_mime(None))
        self.assertIsNone(MIME_PARSER.parse_raw_mime([]))


if __name__ == "__main__":
    unittest.main()
