#!/usr/bin/env python
import webapp2
import mail

app = webapp2.WSGIApplication([
    ('/auth', mail.auth.Handler),
    ('/mail/check', mail.check.Handler),
    ('/mail/list', mail.list.Handler),
    ('/mail/me', mail.list.Single)
], debug=True)
