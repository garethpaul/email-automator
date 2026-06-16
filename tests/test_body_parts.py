# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import unittest
from email import message_from_string


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BODY_PARTS_PATH = os.path.join(ROOT, "mail", "body_parts.py")
try:
    from importlib import util as importlib_util
except ImportError:
    import imp

    BODY_PARTS = imp.load_source("body_parts", BODY_PARTS_PATH)
else:
    SPEC = importlib_util.spec_from_file_location("body_parts", BODY_PARTS_PATH)
    BODY_PARTS = importlib_util.module_from_spec(SPEC)
    SPEC.loader.exec_module(BODY_PARTS)


def selected_payloads(raw_message):
    message = message_from_string(raw_message)
    html, text = BODY_PARTS.select_inline_body_parts(message)
    return [part.get_payload() for part in html], [part.get_payload() for part in text]


class BodyPartTests(unittest.TestCase):
    def test_selects_inline_plain_text_and_html(self):
        raw = """Content-Type: multipart/alternative; boundary=body

--body
Content-Type: text/plain

plain body
--body
Content-Type: text/html

<p>html body</p>
--body--
"""

        self.assertEqual(selected_payloads(raw), (["<p>html body</p>"], ["plain body"]))

    def test_rejects_explicit_text_attachments(self):
        raw = """Content-Type: multipart/mixed; boundary=body

--body
Content-Type: text/plain

real body
--body
Content-Type: text/html
Content-Disposition: attachment

<p>attached override</p>
--body--
"""

        self.assertEqual(selected_payloads(raw), ([], ["real body"]))

    def test_rejects_named_parts_without_disposition(self):
        raw = """Content-Type: multipart/mixed; boundary=body

--body
Content-Type: text/plain

real body
--body
Content-Type: text/plain; name=notes.txt

attached notes
--body--
"""

        self.assertEqual(selected_payloads(raw), ([], ["real body"]))

    def test_rejects_descendants_of_attached_messages(self):
        raw = """Content-Type: multipart/mixed; boundary=outer

--outer
Content-Type: text/plain

real body
--outer
Content-Type: message/rfc822
Content-Disposition: attachment

Content-Type: text/html

<p>attached message body</p>
--outer--
"""

        self.assertEqual(selected_payloads(raw), ([], ["real body"]))

    def test_rejects_descendants_of_undecorated_encapsulated_messages(self):
        raw = """Content-Type: multipart/mixed; boundary=outer

--outer
Content-Type: text/plain

real body
--outer
Content-Type: message/rfc822

Content-Type: text/html

<p>encapsulated override</p>
--outer--
"""

        self.assertEqual(selected_payloads(raw), ([], ["real body"]))

    def test_related_without_start_traverses_only_first_child(self):
        raw = """Content-Type: multipart/related; boundary=related

--related
Content-Type: multipart/alternative; boundary=body

--body
Content-Type: text/plain

plain root
--body
Content-Type: text/html

<p>html root</p>
--body--
--related
Content-Type: text/html
Content-ID: <resource>

<p>related override</p>
--related--
"""

        self.assertEqual(selected_payloads(raw), (["<p>html root</p>"], ["plain root"]))

    def test_related_start_selects_matching_content_id(self):
        raw = """Content-Type: multipart/related; boundary=related; start="<root@message>"

--related
Content-Type: text/html
Content-ID: <resource>

<p>related override</p>
--related
Content-Type: multipart/alternative; boundary=body
Content-ID: <root@message>

--body
Content-Type: text/plain

plain root
--body
Content-Type: text/html

<p>html root</p>
--body--
--related--
"""

        self.assertEqual(selected_payloads(raw), (["<p>html root</p>"], ["plain root"]))

    def test_related_with_unresolved_start_fails_closed(self):
        raw = """Content-Type: multipart/related; boundary=related; start="<missing>"

--related
Content-Type: text/plain
Content-ID: <first>

untrusted fallback
--related
Content-Type: text/html
Content-ID: <second>

<p>related override</p>
--related--
"""

        self.assertEqual(selected_payloads(raw), ([], []))


if __name__ == "__main__":
    unittest.main()
