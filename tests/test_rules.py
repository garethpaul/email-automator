import os
import unittest

from mail import rules


def choose_first(options):
    return options[0]


class RuleTests(unittest.TestCase):
    def setUp(self):
        self._original_env = {
            "AUTOMATION_APPROVED_SENDERS": os.environ.get("AUTOMATION_APPROVED_SENDERS"),
            "AUTOMATION_TO_EMAIL": os.environ.get("AUTOMATION_TO_EMAIL"),
        }
        self._original_from_users = rules.from_users
        os.environ["AUTOMATION_APPROVED_SENDERS"] = "approveduser@approveduser.com"
        os.environ["AUTOMATION_TO_EMAIL"] = "myemail@myemail.com"
        rules.from_users = rules.configured_from_users()
        if hasattr(rules.memcache, "clear"):
            rules.memcache.clear()

    def tearDown(self):
        rules.from_users = self._original_from_users
        for name, value in self._original_env.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value

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

    def test_reply_subject_removes_header_breaks(self):
        subject = rules.reply_subject("Coffee\r\nBcc: attacker@example.com")

        self.assertEqual("Re: Coffee Bcc: attacker@example.com", subject)
        self.assertNotIn("\r", subject)
        self.assertNotIn("\n", subject)

    def test_reply_subject_handles_empty_and_long_subjects(self):
        self.assertEqual("Re:", rules.reply_subject(" \n "))
        subject = rules.reply_subject("x" * (rules.MAX_REPLY_SUBJECT_LENGTH + 20))

        self.assertEqual(4 + rules.MAX_REPLY_SUBJECT_LENGTH, len(subject))

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

    def test_configured_from_users_ignores_invalid_addresses(self):
        original_value = os.environ.get("AUTOMATION_APPROVED_SENDERS")
        os.environ["AUTOMATION_APPROVED_SENDERS"] = (
            "first@example.com,not-an-address,second@example.com\r\nBcc: attacker@example.com"
        )
        try:
            self.assertEqual(["first@example.com"], rules.configured_from_users())
        finally:
            if original_value is None:
                del os.environ["AUTOMATION_APPROVED_SENDERS"]
            else:
                os.environ["AUTOMATION_APPROVED_SENDERS"] = original_value

    def test_configured_to_email_reads_environment(self):
        original_value = os.environ.get("AUTOMATION_TO_EMAIL")
        os.environ["AUTOMATION_TO_EMAIL"] = "Automation@Example.com "
        try:
            self.assertEqual("automation@example.com", rules.configured_to_email())
        finally:
            if original_value is None:
                del os.environ["AUTOMATION_TO_EMAIL"]
            else:
                os.environ["AUTOMATION_TO_EMAIL"] = original_value

    def test_configured_to_email_rejects_invalid_address(self):
        original_value = os.environ.get("AUTOMATION_TO_EMAIL")
        os.environ["AUTOMATION_TO_EMAIL"] = "automation@example.com\r\nBcc: attacker@example.com"
        try:
            self.assertEqual("", rules.configured_to_email())
        finally:
            if original_value is None:
                del os.environ["AUTOMATION_TO_EMAIL"]
            else:
                os.environ["AUTOMATION_TO_EMAIL"] = original_value

    def test_message_addressed_to_automation_matches_address_case_insensitively(self):
        msg = {"to": [("Automation", "Automation@Example.com")]}

        self.assertTrue(rules.message_addressed_to_automation(msg, "automation@example.com"))

    def test_message_addressed_to_automation_ignores_display_name_match(self):
        msg = {"to": [("automation@example.com", "other@example.com")]}

        self.assertFalse(rules.message_addressed_to_automation(msg, "automation@example.com"))

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
            "to": [("Automation", "myemail@myemail.com")],
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

    def test_valid_email_sanitizes_reply_subject(self):
        sent = []
        original_send = rules.sendEmail
        rules.sendEmail = lambda *args: sent.append(args)
        msg = {
            "from": [("Allowed", "approveduser@approveduser.com")],
            "to": [("Automation", "myemail@myemail.com")],
            "msgId": "message-id",
            "subject": "Coffee\r\nBcc: attacker@example.com",
            "payload": "Please ask Gareth",
        }
        try:
            self.assertTrue(rules.valid_email(msg, "user-id"))
        finally:
            rules.sendEmail = original_send

        self.assertEqual("Re: Coffee Bcc: attacker@example.com", sent[0][2])

    def test_valid_email_rejects_message_not_addressed_to_automation(self):
        sent = []
        original_send = rules.sendEmail
        rules.sendEmail = lambda *args: sent.append(args)
        msg = {
            "from": [("Allowed", "approveduser@approveduser.com")],
            "to": [("Other", "other@example.com")],
            "msgId": "message-id",
            "subject": "Coffee",
            "payload": "Please ask Gareth",
        }
        try:
            self.assertFalse(rules.valid_email(msg, "user-id"))
        finally:
            rules.sendEmail = original_send

        self.assertEqual([], sent)


if __name__ == "__main__":
    unittest.main()
