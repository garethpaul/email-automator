from __future__ import unicode_literals

import os
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIST_RESPONSE_PATH = os.path.join(ROOT, "mail", "list_response.py")
try:
    from importlib import util as importlib_util
except ImportError:
    import imp

    LIST_RESPONSE = imp.load_source("list_response", LIST_RESPONSE_PATH)
else:
    SPEC = importlib_util.spec_from_file_location("list_response", LIST_RESPONSE_PATH)
    LIST_RESPONSE = importlib_util.module_from_spec(SPEC)
    SPEC.loader.exec_module(LIST_RESPONSE)


class ListResponseTests(unittest.TestCase):
    def test_absent_messages_returns_empty_list(self):
        self.assertEqual([], LIST_RESPONSE.bounded_message_summaries({}))

    def test_malformed_response_shapes_return_empty_list(self):
        for response in (None, [], "messages", {"messages": None}, {"messages": {}}):
            self.assertEqual([], LIST_RESPONSE.bounded_message_summaries(response))

    def test_tuple_messages_are_preserved_as_a_list(self):
        self.assertEqual(
            [{"id": "one"}, {"id": "two"}],
            LIST_RESPONSE.bounded_message_summaries(
                {"messages": ({"id": "one"}, {"id": "two"})}
            ),
        )

    def test_messages_are_bounded_to_thirty(self):
        messages = [{"id": str(index)} for index in range(31)]

        result = LIST_RESPONSE.bounded_message_summaries({"messages": messages})

        self.assertEqual(messages[:30], result)


if __name__ == "__main__":
    unittest.main()
