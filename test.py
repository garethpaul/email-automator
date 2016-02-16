import unittest
import webapp2
import webtest

import sys
sys.path.append('/usr/local/google_appengine/')

from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import testbed
from google.appengine.api import users

#
from django.conf import settings
settings.configure()

import mail.auth

class TestHandlers(unittest.TestCase):
    def setUp(self):
        app = webapp2.WSGIApplication([('/', mail.auth.Handler)])
        self.testapp = webtest.TestApp(app)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_user_stub()

    def loginUser(self, email='user@example.com', id='123', is_admin=False):
        self.testbed.setup_env(
            user_email=email,
            user_id=id,
            user_is_admin='1' if is_admin else '0',
            overwrite=True)

    def test_hello(self):
        assert not users.get_current_user()
        self.loginUser
        #response = self.testapp.get('/')

    def tearDown(self):
        self.testbed.deactivate()


if __name__ == '__main__':
    unittest.main()
