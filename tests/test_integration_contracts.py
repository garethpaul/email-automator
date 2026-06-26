from __future__ import unicode_literals

import os
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_source(relative_path):
    path = os.path.join(ROOT, relative_path)
    with open(path, "r") as source_file:
        return source_file.read()


class IntegrationContractTests(unittest.TestCase):
    def test_gmail_list_response_is_bounded_and_http_errors_return_empty_list(self):
        source = read_source("mail/list.py")
        handler = source.split("def ListMessagesWithLabels", 1)[1].split(
            "def GetThread", 1
        )[0]

        self.assertIn("from .list_response import bounded_message_summaries", source)
        self.assertIn("for msg in bounded_message_summaries(response):", handler)
        self.assertNotIn("if 'messages' in response:", handler)
        self.assertIn("except errors.HttpError, error:", handler)
        self.assertTrue(handler.rstrip().endswith("return []"))

    def test_mime_boundary_failure_drops_message_without_crashing_scan(self):
        source = read_source("mail/list.py")

        self.assertIn("msg = parse_raw_mime(msg_str)", source)
        self.assertIn("if msg is None:\n        return None", source)
        self.assertNotIn("raise Exception('No suitable part found')", source)

    def test_send_module_delegates_reply_encoding_to_guarded_helper(self):
        source = read_source("mail/send.py")

        self.assertIn("return create_message(sender, to, subject, message_text)", source)
        self.assertNotIn("base64.b64encode(message.as_string())", source)


if __name__ == "__main__":
    unittest.main()
