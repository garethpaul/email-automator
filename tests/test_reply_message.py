# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
from email import message_from_string
import os
import re
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPLY_MESSAGE_PATH = os.path.join(ROOT, "mail", "reply_message.py")
try:
    from importlib import util as importlib_util
except ImportError:
    import imp

    REPLY_MESSAGE = imp.load_source("reply_message", REPLY_MESSAGE_PATH)
else:
    SPEC = importlib_util.spec_from_file_location("reply_message", REPLY_MESSAGE_PATH)
    REPLY_MESSAGE = importlib_util.module_from_spec(SPEC)
    SPEC.loader.exec_module(REPLY_MESSAGE)


class ReplyMessageTests(unittest.TestCase):
    def test_raw_message_encoding_uses_base64url_alphabet(self):
        self.assertEqual(REPLY_MESSAGE.encode_raw_message(b"\x00\x00>"), "AAA-")

    def test_builds_decodable_plain_text_reply(self):
        result = REPLY_MESSAGE.create_message(
            "robot@example.com",
            "person@example.com",
            "Re: hello",
            "reply body",
        )

        self.assertTrue(re.match(r"^[A-Za-z0-9_-]+={0,2}$", result["raw"]))
        decoded = base64.urlsafe_b64decode(result["raw"].encode("ascii"))
        message = message_from_string(decoded.decode("ascii"))
        self.assertEqual(message.get("From"), "robot@example.com")
        self.assertEqual(message.get("To"), "person@example.com")
        self.assertEqual(message.get("Subject"), "Re: hello")
        self.assertEqual(message.get_payload(), "reply body")

    def test_rejects_injected_reply_headers(self):
        fields = (
            ("robot@example.com\r\nBcc: attacker@example.com", "person@example.com", "subject"),
            ("robot@example.com", "person@example.com\nBcc: attacker@example.com", "subject"),
            ("robot@example.com", "person@example.com", "subject\r\nBcc: attacker@example.com"),
            ("robot@example.com", "person@example.com", "subject\x00hidden"),
        )
        for sender, recipient, subject in fields:
            with self.assertRaises(ValueError):
                REPLY_MESSAGE.create_message(sender, recipient, subject, "body")


if __name__ == "__main__":
    unittest.main()
