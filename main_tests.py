import importlib
import os
import sys
import types
import unittest


class FakeWSGIApplication(object):
    def __init__(self, routes, debug=False):
        self.routes = routes
        self.debug = debug


def install_fake_dependencies():
    webapp2 = types.ModuleType('webapp2')
    webapp2.WSGIApplication = FakeWSGIApplication
    sys.modules['webapp2'] = webapp2

    mail = types.ModuleType('mail')
    mail.__path__ = []
    sys.modules['mail'] = mail

    for name in ('auth', 'check', 'list'):
        module = types.ModuleType('mail.{0}'.format(name))
        module.Handler = object
        if name == 'list':
            module.Single = object
        setattr(mail, name, module)
        sys.modules['mail.{0}'.format(name)] = module


def load_main():
    sys.modules.pop('main', None)
    install_fake_dependencies()
    return importlib.import_module('main')


class MainDebugTest(unittest.TestCase):
    def setUp(self):
        self.original_debug = os.environ.get('EMAIL_AUTOMATOR_DEBUG')

    def tearDown(self):
        if self.original_debug is None:
            os.environ.pop('EMAIL_AUTOMATOR_DEBUG', None)
        else:
            os.environ['EMAIL_AUTOMATOR_DEBUG'] = self.original_debug
        sys.modules.pop('main', None)

    def test_debug_is_disabled_by_default(self):
        os.environ.pop('EMAIL_AUTOMATOR_DEBUG', None)

        main = load_main()

        self.assertFalse(main.app.debug)

    def test_debug_requires_explicit_truthy_env(self):
        os.environ['EMAIL_AUTOMATOR_DEBUG'] = 'true'

        main = load_main()

        self.assertTrue(main.app.debug)

    def test_debug_rejects_falsey_env(self):
        os.environ['EMAIL_AUTOMATOR_DEBUG'] = 'false'

        main = load_main()

        self.assertFalse(main.app.debug)


if __name__ == '__main__':
    unittest.main()
