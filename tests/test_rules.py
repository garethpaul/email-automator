import os
import unittest

from mail import rules


def choose_first(options):
    return options[0]


class RuleTests(unittest.TestCase):
    def setUp(self):
        if hasattr(rules.memcache, "clear"):
            rules.memcache.clear()

    def test_keyword_reply_is_deterministic_with_injected_choice(self):
        reply = rules.parse_email("Can you ask Gareth, about this?", chooser=choose_first)

        self.assertIn("Gareth", reply)
        self.assertIn("coffee", reply)
        self.assertTrue(reply.startswith(rules.cheeky[0]))
        self.assertTrue(reply.endswith(rules.ending[0]))

    def test_unknown_reply_does_not_use_emergency_language(self):
        reply = rules.parse_email("unmatched words", chooser=choose_first)

        self.assertIn("contact me directly", reply)
        self.assertNotIn("911", reply)

    def test_approved_sender_returns_allowed_address(self):
        msg = {"from": [("Allowed", "approveduser@approveduser.com")]}

        self.assertEqual("approveduser@approveduser.com", rules.approved_sender(msg))

    def test_approved_sender_matches_address_case_insensitively(self):
        msg = {"from": [("Allowed", "ApprovedUser@ApprovedUser.com")]}

        self.assertEqual("ApprovedUser@ApprovedUser.com", rules.approved_sender(msg))

    def test_approved_sender_rejects_unknown_address(self):
        msg = {"from": [("Unknown", "stranger@example.com")]}

        self.assertIsNone(rules.approved_sender(msg))

    def test_configured_from_users_reads_environment(self):
        original_value = os.environ.get("AUTOMATION_APPROVED_SENDERS")
        os.environ["AUTOMATION_APPROVED_SENDERS"] = "first@example.com, second@example.com, "
        try:
            self.assertEqual(
                ["first@example.com", "second@example.com"],
                rules.configured_from_users()
            )
        finally:
            if original_value is None:
                del os.environ["AUTOMATION_APPROVED_SENDERS"]
            else:
                os.environ["AUTOMATION_APPROVED_SENDERS"] = original_value

    def test_cache_check_allows_when_memcache_unavailable(self):
        original_memcache = rules.memcache
        rules.memcache = None
        try:
            self.assertTrue(rules.cache_check("message-id"))
        finally:
            rules.memcache = original_memcache

    def test_valid_email_sends_approved_message_once(self):
        sent = []
        original_send = rules.sendEmail
        rules.sendEmail = lambda *args: sent.append(args)
        msg = {
            "from": [("Allowed", "approveduser@approveduser.com")],
            "msgId": "message-id",
            "subject": "Coffee",
            "payload": "Please ask Gareth",
        }
        try:
            self.assertTrue(rules.valid_email(msg, "user-id"))
            self.assertFalse(rules.valid_email(msg, "user-id"))
        finally:
            rules.sendEmail = original_send

        self.assertEqual(1, len(sent))
        self.assertEqual("approveduser@approveduser.com", sent[0][1])
        self.assertEqual("Re: Coffee", sent[0][2])


if __name__ == "__main__":
    unittest.main()
