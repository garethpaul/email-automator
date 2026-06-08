#!/usr/bin/env python
import os
import sys
sys.path.append('/usr/local/google_appengine/')

import webapp2
import mail
import mail.auth
import mail.check
import mail.list

DEBUG_ENV_VAR = 'EMAIL_AUTOMATOR_DEBUG'
DEBUG_TRUE_VALUES = {'1', 'true', 'yes', 'on'}


def debug_enabled():
    return os.environ.get(DEBUG_ENV_VAR, '').lower() in DEBUG_TRUE_VALUES


app = webapp2.WSGIApplication([
    ('/auth', mail.auth.Handler),
    ('/mail/check', mail.check.Handler),
    ('/mail/list', mail.list.Handler),
    ('/mail/me', mail.list.Single)
], debug=debug_enabled())


if __name__ == '__main__':
    unittest.main()
