from __future__ import absolute_import

import os
import sys
import types
import unittest


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_PATH = os.path.join(ROOT_DIR, "database", "cache.py")


class FakeMemcache(object):
    def __init__(self):
        self.calls = []

    def get(self, key):
        return key

    def add(self, key, value, duration):
        self.calls.append((key, value, duration))
        return True


class CacheTest(unittest.TestCase):
    def setUp(self):
        self.fake_memcache = FakeMemcache()
        google = types.ModuleType("google")
        appengine = types.ModuleType("google.appengine")
        api = types.ModuleType("google.appengine.api")
        api.memcache = self.fake_memcache
        google.appengine = appengine
        appengine.api = api
        self.previous_modules = {}
        for name, module in (
            ("google", google),
            ("google.appengine", appengine),
            ("google.appengine.api", api),
        ):
            self.previous_modules[name] = sys.modules.get(name)
            sys.modules[name] = module

    def tearDown(self):
        for name, module in self.previous_modules.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module

    def test_add_forwards_requested_duration(self):
        cache = types.ModuleType("email_automator_cache_test")
        cache.__file__ = CACHE_PATH
        with open(CACHE_PATH, "rb") as cache_file:
            source = cache_file.read()
        eval(compile(source, CACHE_PATH, "exec"), cache.__dict__)

        self.assertTrue(cache.add("key", "value", 17))
        self.assertEqual([("key", "value", 17)], self.fake_memcache.calls)


if __name__ == "__main__":
    unittest.main()
