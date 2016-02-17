#!/usr/bin/env python
import sys
sys.path.append('/usr/local/google_appengine/')

import webapp2
import mail
import mail.auth
import mail.check
import mail.list

app = webapp2.WSGIApplication([
    ('/auth', mail.auth.Handler),
    ('/mail/check', mail.check.Handler),
    ('/mail/list', mail.list.Handler),
    ('/mail/me', mail.list.Single)
], debug=True)


if __name__ == '__main__':
    unittest.main()
