from contextlib import contextmanager
import os
import unittest

from mail import rules


def choose_first(options):
    return options[0]


class CompatibleTestCase(unittest.TestCase):
    if not hasattr(unittest.TestCase, "subTest"):
        @contextmanager
        def subTest(self, **params):
            del params
            yield


class RuleTests(CompatibleTestCase):
    def setUp(self):
        self._original_env = {
            "AUTOMATION_APPROVED_SENDERS": os.environ.get("AUTOMATION_APPROVED_SENDERS"),
            "AUTOMATION_TO_EMAIL": os.environ.get("AUTOMATION_TO_EMAIL"),
            "AUTOMATION_FROM_EMAIL": os.environ.get("AUTOMATION_FROM_EMAIL"),
        }
        os.environ["AUTOMATION_APPROVED_SENDERS"] = "approveduser@approveduser.com"
        os.environ["AUTOMATION_TO_EMAIL"] = "myemail@myemail.com"
        os.environ["AUTOMATION_FROM_EMAIL"] = "youremail@youremail.com"
        if hasattr(rules.memcache, "clear"):
            rules.memcache.clear()

    def tearDown(self):
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

    def test_tokenize_email_ignores_text_after_body_limit(self):
        body = (" " * rules.MAX_EMAIL_BODY_LENGTH) + "Gareth"

        self.assertEqual([], rules.tokenize_email(body))

    def test_rule_matching_treats_malformed_body_values_as_empty(self):
        for body in (None, 42, [], {}, object()):
            with self.subTest(body=body):
                self.assertEqual([], rules.tokenize_email(body))
                reply = rules.parse_email(body, chooser=choose_first)
                self.assertIn(rules.unknown[0], reply)

    def test_reply_subject_removes_header_breaks(self):
        subject = rules.reply_subject("Coffee\r\nBcc: attacker@example.com")

        self.assertEqual("Re: Coffee Bcc: attacker@example.com", subject)
        self.assertNotIn("\r", subject)
        self.assertNotIn("\n", subject)

    def test_reply_subject_handles_empty_and_long_subjects(self):
        self.assertEqual("Re:", rules.reply_subject(" \n "))
        subject = rules.reply_subject("x" * (rules.MAX_REPLY_SUBJECT_LENGTH + 20))

        self.assertEqual(4 + rules.MAX_REPLY_SUBJECT_LENGTH, len(subject))

    def test_reply_subject_treats_malformed_values_as_empty(self):
        for subject in (None, 42, [], {}, object()):
            with self.subTest(subject=subject):
                self.assertEqual("Re:", rules.reply_subject(subject))

    def test_approved_sender_returns_allowed_address(self):
        msg = {"from": [("Allowed", "approveduser@approveduser.com")]}

        self.assertEqual("approveduser@approveduser.com", rules.approved_sender(msg))

    def test_approved_sender_matches_address_case_insensitively(self):
        msg = {"from": [("Allowed", "ApprovedUser@ApprovedUser.com")]}

        self.assertEqual("ApprovedUser@ApprovedUser.com", rules.approved_sender(msg))

    def test_approved_sender_uses_current_environment_allowlist(self):
        old_sender = {"from": [("Old", "approveduser@approveduser.com")]}
        new_sender = {"from": [("New", "new@example.com")]}

        self.assertEqual(
            "approveduser@approveduser.com",
            rules.approved_sender(old_sender),
        )

        os.environ["AUTOMATION_APPROVED_SENDERS"] = "new@example.com"

        self.assertIsNone(rules.approved_sender(old_sender))
        self.assertEqual("new@example.com", rules.approved_sender(new_sender))

    def test_approved_sender_rejects_configured_automation_address(self):
        os.environ["AUTOMATION_APPROVED_SENDERS"] = (
            "robot@example.com, approveduser@approveduser.com"
        )
        os.environ["AUTOMATION_FROM_EMAIL"] = "  Robot@Example.com  "
        self_message = {
            "from": [("Robot", "ROBOT@example.com")]
        }
        allowed_message = {
            "from": [("Allowed", "approveduser@approveduser.com")]
        }

        self.assertIsNone(rules.approved_sender(self_message))
        self.assertEqual(
            "approveduser@approveduser.com",
            rules.approved_sender(allowed_message),
        )

    def test_approved_sender_fails_closed_when_self_address_precedes_allowed_address(self):
        os.environ["AUTOMATION_APPROVED_SENDERS"] = (
            "robot@example.com, approveduser@approveduser.com"
        )
        os.environ["AUTOMATION_FROM_EMAIL"] = "robot@example.com"
        msg = {
            "from": [
                ("Robot", "robot@example.com"),
                ("Allowed", "approveduser@approveduser.com"),
            ]
        }

        self.assertIsNone(rules.approved_sender(msg))

    def test_approved_sender_fails_closed_when_self_address_follows_allowed_address(self):
        os.environ["AUTOMATION_APPROVED_SENDERS"] = (
            "robot@example.com, approveduser@approveduser.com"
        )
        os.environ["AUTOMATION_FROM_EMAIL"] = "robot@example.com"
        msg = {
            "from": [
                ("Allowed", "approveduser@approveduser.com"),
                ("Robot", "robot@example.com"),
            ]
        }

        self.assertIsNone(rules.approved_sender(msg))

    def test_approved_sender_refreshes_automation_address(self):
        os.environ["AUTOMATION_APPROVED_SENDERS"] = "first@example.com, second@example.com"
        first = {"from": [("First", "first@example.com")]}
        second = {"from": [("Second", "second@example.com")]}

        os.environ["AUTOMATION_FROM_EMAIL"] = "first@example.com"
        self.assertIsNone(rules.approved_sender(first))
        self.assertEqual("second@example.com", rules.approved_sender(second))

        os.environ["AUTOMATION_FROM_EMAIL"] = "second@example.com"
        self.assertEqual("first@example.com", rules.approved_sender(first))
        self.assertIsNone(rules.approved_sender(second))

    def test_approved_sender_rejects_unknown_address(self):
        msg = {"from": [("Unknown", "stranger@example.com")]}

        self.assertIsNone(rules.approved_sender(msg))

    def test_approved_sender_ignores_malformed_entries(self):
        msg = {
            "from": [
                None,
                ("Only",),
                ("Too", "Many", "Values"),
                "not-an-address-pair",
                ("Numeric", 42),
            ]
        }

        self.assertIsNone(rules.approved_sender(msg))

    def test_approved_sender_rejects_malformed_sender_collections(self):
        malformed_collections = (
            None,
            42,
            "not-an-address-list",
            {"address": "approveduser@approveduser.com"},
        )
        for senders in malformed_collections:
            with self.subTest(senders=senders):
                self.assertIsNone(rules.approved_sender({"from": senders}))

    def test_approved_sender_accepts_valid_entry_after_malformed_entries(self):
        msg = {
            "from": [
                None,
                ("Only",),
                ("Allowed", "ApprovedUser@ApprovedUser.com"),
            ]
        }

        self.assertEqual(
            "ApprovedUser@ApprovedUser.com",
            rules.approved_sender(msg),
        )

    def test_approved_sender_rejects_duplicate_valid_entries(self):
        msg = {
            "from": [
                ("Allowed", "approveduser@approveduser.com"),
                ("Duplicate", "approveduser@approveduser.com"),
            ]
        }

        self.assertIsNone(rules.approved_sender(msg))

    def test_approved_sender_rejects_mixed_valid_entries_in_any_order(self):
        allowed = ("Allowed", "approveduser@approveduser.com")
        unknown = ("Unknown", "stranger@example.com")

        for senders in ([allowed, unknown], [unknown, allowed]):
            with self.subTest(senders=senders):
                self.assertIsNone(rules.approved_sender({"from": senders}))

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

    def test_configured_from_email_reads_environment(self):
        original_value = os.environ.get("AUTOMATION_FROM_EMAIL")
        os.environ["AUTOMATION_FROM_EMAIL"] = "Robot@Example.com "
        try:
            self.assertEqual("robot@example.com", rules.configured_from_email())
        finally:
            if original_value is None:
                del os.environ["AUTOMATION_FROM_EMAIL"]
            else:
                os.environ["AUTOMATION_FROM_EMAIL"] = original_value

    def test_configured_from_email_rejects_invalid_address(self):
        original_value = os.environ.get("AUTOMATION_FROM_EMAIL")
        os.environ["AUTOMATION_FROM_EMAIL"] = "robot@example.com\r\nBcc: attacker@example.com"
        try:
            self.assertEqual("", rules.configured_from_email())
        finally:
            if original_value is None:
                del os.environ["AUTOMATION_FROM_EMAIL"]
            else:
                os.environ["AUTOMATION_FROM_EMAIL"] = original_value

    def test_send_email_rejects_invalid_from_email_before_importing_sender(self):
        os.environ["AUTOMATION_FROM_EMAIL"] = "robot@example.com\r\nBcc: attacker@example.com"

        self.assertFalse(rules.sendEmail("user-id", "approveduser@approveduser.com", "Subject", "Body"))

    def test_message_addressed_to_automation_matches_address_case_insensitively(self):
        msg = {"to": [("Automation", "Automation@Example.com")]}

        self.assertTrue(rules.message_addressed_to_automation(msg, "automation@example.com"))

    def test_message_addressed_to_automation_ignores_display_name_match(self):
        msg = {"to": [("automation@example.com", "other@example.com")]}

        self.assertFalse(rules.message_addressed_to_automation(msg, "automation@example.com"))

    def test_message_addressed_to_automation_rejects_malformed_containers(self):
        self.assertFalse(rules.message_addressed_to_automation(None, "automation@example.com"))
        self.assertFalse(
            rules.message_addressed_to_automation(
                {"to": "automation@example.com"}, "automation@example.com"
            )
        )

    def test_message_addressed_to_automation_skips_malformed_addresses(self):
        msg = {
            "to": [
                None,
                ("Only",),
                ("Malformed", object()),
                ("Automation", "Automation@Example.com"),
            ]
        }

        self.assertTrue(rules.message_addressed_to_automation(msg, "automation@example.com"))

    def test_cache_check_allows_when_memcache_unavailable(self):
        original_memcache = rules.memcache
        rules.memcache = None
        try:
            self.assertTrue(rules.cache_check("message-id"))
        finally:
            rules.memcache = original_memcache

    def test_cache_key_rejects_malformed_message_ids(self):
        self.assertEqual("msg_message-id:123", rules.cache_key(" message-id:123 "))
        self.assertIsNone(rules.cache_key("message-id\r\nother"))
        self.assertIsNone(rules.cache_key("x" * (rules.MAX_MESSAGE_ID_LENGTH + 1)))

    def test_gmail_message_id_uses_message_id_not_thread_id(self):
        summary = {"id": " message-123 ", "threadId": "thread-456"}

        self.assertEqual("message-123", rules.gmail_message_id(summary))

    def test_gmail_message_id_rejects_malformed_summaries(self):
        malformed = [
            None,
            [],
            {"threadId": "thread-only"},
            {"id": 123},
            {"id": "message-id\r\nother"},
            {"id": "x" * (rules.MAX_MESSAGE_ID_LENGTH + 1)},
        ]

        for summary in malformed:
            with self.subTest(summary=summary):
                self.assertEqual("", rules.gmail_message_id(summary))

    def test_valid_email_sends_approved_message_once(self):
        sent = []
        original_send = rules.sendEmail
        rules.sendEmail = lambda *args: sent.append(args) or True
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

    def test_valid_email_reserves_message_before_sending(self):
        sent = []
        nested_results = []
        original_send = rules.sendEmail
        msg = {
            "from": [("Allowed", "approveduser@approveduser.com")],
            "to": [("Automation", "myemail@myemail.com")],
            "msgId": "message-id",
            "subject": "Coffee",
            "payload": "Please ask Gareth",
        }

        def send_with_concurrent_attempt(*args):
            sent.append(args)
            if len(sent) == 1:
                nested_results.append(rules.valid_email(msg, "user-id"))
            return True

        rules.sendEmail = send_with_concurrent_attempt
        try:
            self.assertTrue(rules.valid_email(msg, "user-id"))
        finally:
            rules.sendEmail = original_send

        self.assertEqual([False], nested_results)
        self.assertEqual(1, len(sent))

    def test_valid_email_releases_reservation_after_failed_send(self):
        attempts = []
        original_send = rules.sendEmail
        msg = {
            "from": [("Allowed", "approveduser@approveduser.com")],
            "to": [("Automation", "myemail@myemail.com")],
            "msgId": "message-id",
            "subject": "Coffee",
            "payload": "Please ask Gareth",
        }

        def fail_once(*args):
            attempts.append(args)
            return len(attempts) > 1

        rules.sendEmail = fail_once
        try:
            self.assertFalse(rules.valid_email(msg, "user-id"))
            self.assertTrue(rules.cache_check("message-id"))
            self.assertTrue(rules.valid_email(msg, "user-id"))
        finally:
            rules.sendEmail = original_send

        self.assertEqual(2, len(attempts))

    def test_valid_email_releases_reservation_after_send_exception(self):
        original_send = rules.sendEmail
        msg = {
            "from": [("Allowed", "approveduser@approveduser.com")],
            "to": [("Automation", "myemail@myemail.com")],
            "msgId": "message-id",
            "subject": "Coffee",
            "payload": "Please ask Gareth",
        }

        def raise_send_error(*args):
            raise RuntimeError("send failed")

        rules.sendEmail = raise_send_error
        try:
            with self.assertRaises(RuntimeError):
                rules.valid_email(msg, "user-id")
        finally:
            rules.sendEmail = original_send

        self.assertTrue(rules.cache_check("message-id"))

    def test_valid_email_sanitizes_reply_subject(self):
        sent = []
        original_send = rules.sendEmail
        rules.sendEmail = lambda *args: sent.append(args) or True
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
        rules.sendEmail = lambda *args: sent.append(args) or True
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

    def test_valid_email_rejects_malformed_recipient_metadata_without_side_effects(self):
        sent = []
        original_send = rules.sendEmail
        rules.sendEmail = lambda *args: sent.append(args) or True
        msg = {
            "from": [("Allowed", "approveduser@approveduser.com")],
            "to": object(),
            "msgId": "malformed-recipient-message",
            "subject": "Coffee",
            "payload": "Please ask Gareth",
        }
        try:
            self.assertFalse(rules.valid_email(msg, "user-id"))
        finally:
            rules.sendEmail = original_send

        self.assertEqual([], sent)
        self.assertTrue(rules.cache_check("malformed-recipient-message"))

    def test_valid_email_rejects_automation_sender_before_reservation(self):
        os.environ["AUTOMATION_APPROVED_SENDERS"] = "robot@example.com"
        os.environ["AUTOMATION_FROM_EMAIL"] = "robot@example.com"
        sent = []
        original_send = rules.sendEmail
        rules.sendEmail = lambda *args: sent.append(args) or True
        msg = {
            "from": [("Robot", "robot@example.com")],
            "to": [("Automation", "myemail@myemail.com")],
            "msgId": "self-generated-message",
            "subject": "Re: Coffee",
            "payload": "Automated reply",
        }
        try:
            self.assertFalse(rules.valid_email(msg, "user-id"))
        finally:
            rules.sendEmail = original_send

        self.assertEqual([], sent)
        self.assertTrue(rules.cache_check("self-generated-message"))

    def test_valid_email_rejects_malformed_sender_metadata_without_side_effects(self):
        sent = []
        original_send = rules.sendEmail
        rules.sendEmail = lambda *args: sent.append(args) or True
        msg = {
            "from": [None, ("Only",), "not-an-address-pair"],
            "to": [("Automation", "myemail@myemail.com")],
            "msgId": "malformed-sender-message",
            "subject": "Coffee",
            "payload": "Please ask Gareth",
        }
        try:
            self.assertFalse(rules.valid_email(msg, "user-id"))
        finally:
            rules.sendEmail = original_send

        self.assertEqual([], sent)
        self.assertTrue(rules.cache_check("malformed-sender-message"))

    def test_valid_email_rejects_ambiguous_sender_metadata_without_side_effects(self):
        sent = []
        original_send = rules.sendEmail
        rules.sendEmail = lambda *args: sent.append(args) or True
        msg = {
            "from": [
                ("Allowed", "approveduser@approveduser.com"),
                ("Unknown", "stranger@example.com"),
            ],
            "to": [("Automation", "myemail@myemail.com")],
            "msgId": "ambiguous-sender-message",
            "subject": "Coffee",
            "payload": "Please ask Gareth",
        }
        try:
            self.assertFalse(rules.valid_email(msg, "user-id"))
        finally:
            rules.sendEmail = original_send

        self.assertEqual([], sent)
        self.assertTrue(rules.cache_check("ambiguous-sender-message"))

    def test_valid_email_rejects_invalid_from_email(self):
        os.environ["AUTOMATION_FROM_EMAIL"] = "robot@example.com\r\nBcc: attacker@example.com"
        msg = {
            "from": [("Allowed", "approveduser@approveduser.com")],
            "to": [("Automation", "myemail@myemail.com")],
            "msgId": "message-id",
            "subject": "Coffee",
            "payload": "Please ask Gareth",
        }

        self.assertFalse(rules.valid_email(msg, "user-id"))
        self.assertTrue(rules.cache_check("message-id"))

    def test_valid_email_rejects_invalid_message_id(self):
        sent = []
        original_send = rules.sendEmail
        rules.sendEmail = lambda *args: sent.append(args) or True
        msg = {
            "from": [("Allowed", "approveduser@approveduser.com")],
            "to": [("Automation", "myemail@myemail.com")],
            "msgId": "message-id\r\nother",
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
