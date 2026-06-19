from __future__ import unicode_literals

import os
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class LegacyHttplib2SecurityTests(unittest.TestCase):
    def test_tls_socket_wrapper_selects_tls_protocol_explicitly(self):
        path = os.path.join(ROOT, "libs", "httplib2", "__init__.py")
        with open(path, "r") as source_file:
            source = source_file.read()

        self.assertIn("ssl_version=ssl.PROTOCOL_TLS", source)


if __name__ == "__main__":
    unittest.main()
