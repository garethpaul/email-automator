#!/usr/bin/env python
import os
import sys
sys.path.append('/usr/local/google_appengine/')

import webapp2
import mail
import mail.auth
import mail.check
import mail.list

DEBUG = os.environ.get('APP_DEBUG') == '1'

app = webapp2.WSGIApplication([
    ('/auth', mail.auth.Handler),
    ('/mail/check', mail.check.Handler),
    ('/mail/list', mail.list.Handler),
    ('/mail/me', mail.list.Single)
], debug=DEBUG)


if __name__ == '__main__':
    print('Run this application with the App Engine development server.')
