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

def request_user_id(handler):
    userId = os.environ.get("AUTOMATION_USER_ID")
    if not userId:
        handler.error(400)
        handler.response.out.write(json.dumps({"error": "Missing automation user id"}))
        return None
    return userId

class Handler(webapp.RequestHandler):
    def get(self):
        # set the headers to return valid format for JSON
        self.response.headers.add_header('Content-Type', 'application/json')
        userId = request_user_id(self)
        if userId is None:
            return
        # perform API request to get list if labels
        results = service.users().labels().list(userId='me').execute(http=auth.getAuth(userId))
        # get the labels
        labels = results.get('labels', [])
        # reuturn the labels back to the user
        self.response.out.write(json.dumps(labels))
