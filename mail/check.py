import webapp2, jinja2, os, time, json, httplib2, sys
import auth
from datetime import datetime
from google.appengine.api import memcache
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from oauth2client.appengine import OAuth2Decorator
from oauth2client.appengine import oauth2decorator_from_clientsecrets
from oauth2client.client import AccessTokenRefreshError
from googleapiclient.discovery import build
sys.path.insert(0, 'libs')
import httplib2

http = httplib2.Http(memcache)
service = build("gmail", "v1", http=http)

class Handler(webapp.RequestHandler):
    def get(self):
        # set the headers to return valid format for JSON
        self.response.headers.add_header('Content-Type', 'application/json')
        # Only use the Google account authenticated by App Engine for Gmail access.
        userId = auth.current_user_id()
        if userId is None:
            self.error(401)
            self.response.out.write(json.dumps({'error': 'authentication required'}))
            return
        # perform API request to get list if labels
        try:
            results = service.users().labels().list(userId='me').execute(http=auth.getAuth(userId))
        except AccessTokenRefreshError:
            self.error(401)
            self.response.out.write(json.dumps({'error': 'gmail authorization required'}))
            return
        # get the labels
        labels = results.get('labels', [])
        # reuturn the labels back to the user
        self.response.out.write(labels)
