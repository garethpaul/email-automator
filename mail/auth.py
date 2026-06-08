import webapp2, jinja2, os, logging, sys
# Get Libs from Sys
sys.path.insert(0, 'libs')
import httplib2

from database import default
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from oauth2client.appengine import OAuth2Decorator
from oauth2client.appengine import oauth2decorator_from_clientsecrets
from oauth2client.client import AccessTokenRefreshError
from oauth2client.appengine import CredentialsModel
from oauth2client.appengine import StorageByKeyName
from oauth2client.tools import run
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users


http = httplib2.Http(memcache)
CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', 'CLIENT ID')
CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', 'CLIENT_SECRET')

decorator = OAuth2Decorator(
  client_id=CLIENT_ID,
  client_secret=CLIENT_SECRET,
  scope=[
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send'
  ], approval_prompt = 'force')

def getAuth(userId):
    if not userId:
        webapp2.abort(400, detail='Missing userId for stored Gmail credentials')
    credentials = StorageByKeyName(default.CredentialsModel, userId, 'credentials').get()
    if credentials is None:
        webapp2.abort(401, detail='No stored Gmail credentials for userId')
    http = httplib2.Http()
    http = credentials.authorize(http)
    return http

class Handler(webapp.RequestHandler):
    @decorator.oauth_required
    def get(self):
        current_user = users.get_current_user()
        self.response.out.write("""<html><body><p>Auth complete!</p></body></html>""")
