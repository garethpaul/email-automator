# Import Global Libs
import webapp2, jinja2, os, json, logging, re, email, sys, logging
# Import Local Libs
import auth, rules
from text_payload import decode_text_payload
try:
    from .raw_message import decode_raw_message
except (ImportError, ValueError):
    from raw_message import decode_raw_message
from database import default

# Get Libs from Sys
sys.path.insert(0, 'libs')
from bs4 import BeautifulSoup
import httplib2

from datetime import datetime, timedelta
from apiclient import errors
from apiclient.discovery import build
from oauth2client.appengine import OAuth2Decorator
from oauth2client.appengine import oauth2decorator_from_clientsecrets
from oauth2client.client import AccessTokenRefreshError
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from email import message_from_string
from email.mime.text import MIMEText
from email.Utils import parseaddr
from email.Header import decode_header

http = httplib2.Http(memcache)
service = build("gmail", "v1", http=http)

atom_rfc2822=r"[a-zA-Z0-9_!#\$\%&'*+/=?\^`{}~|\-]+"
atom_posfix_restricted=r"[a-zA-Z0-9_#\$&'*+/=?\^`{}~|\-]+" # without '!' and '%'
atom=atom_rfc2822
dot_atom=atom  +  r"(?:\."  +  atom  +  ")*"
quoted=r'"(?:\\[^\r\n]|[^\\"])*"'
local="(?:"  +  dot_atom  +  "|"  +  quoted  +  ")"
domain_lit=r"\[(?:\\\S|[\x21-\x5a\x5e-\x7e])*\]"
domain="(?:"  +  dot_atom  +  "|"  +  domain_lit  +  ")"
addr_spec=local  +  "\@"  +  domain
email_address_re=re.compile('^'+addr_spec+'$')

def request_user_id(handler):
    userId = (os.environ.get("AUTOMATION_USER_ID") or "").strip()
    if not userId:
        handler.error(400)
        handler.response.out.write(json.dumps({"error": "Missing automation user id"}))
        return None
    return userId

def ListMessagesWithLabels(service, user_id, label_ids=[]):
  """List all Messages of the user's mailbox with label_ids applied.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    label_ids: Only return Messages with these labelIds applied.

  Returns:
    List of Messages that have all required Labels applied. Note that the
    returned list contains Message IDs, you must use get with the
    appropriate id to get the details of a Message.
  """
  try:
    response = service.users().messages().list(userId='me',
                                               labelIds=label_ids).execute(http=auth.getAuth(user_id))
    messages = []
    if 'messages' in response:
        msgs = response['messages']
        for msg in msgs[:30]:
            message_id = rules.gmail_message_id(msg)
            if not message_id:
                continue
            cache_key = "messageId_" + message_id
            _cache = memcache.get(cache_key)
            if _cache is not None:
                messages.append(_cache)
            else:
                mail_msg = GetMimeMessage(service, user_id, message_id)
                if mail_msg is not None:
                    memcache.add(cache_key, mail_msg)
                    messages.append(mail_msg)
    return messages
  except errors.HttpError, error:
    print 'An error occurred: %s' % error

def GetThread(user_id, thread_id):
  """Get a Thread.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    thread_id: The ID of the Thread required.

  Returns:
    Thread with matching ID.
  """
  try:
    thread = service.users().threads().get(userId='me', id=thread_id).execute(http=auth.getAuth(user_id))
    messages = thread['messages']
    print ('thread id: %s - number of messages '
           'in this thread: %d') % (thread['id'], len(messages))
    return thread
  except errors.HttpError, error:
    print 'An error occurred: %s' % error

def GetMessage(user_id, msg_id):
  """Get a Message with given ID.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

  Returns:
    A Message.
  """
  try:
    message = service.users().messages().get(userId='me', id=msg_id).execute(http=auth.getAuth(user_id))
    return message
  except errors.HttpError, error:
    print 'An error occurred: %s' % error

def get_mpart(mail):
    maintype = mail.get_content_maintype()
    if maintype == 'text':
        return mail.get_payload()

def get_mail_body(mail):
    """
    There is no 'body' tag in mail, so separate function.
    :param mail: Message object
    :return: Body content
    """
    body = ""
    if mail.is_multipart():
        body = get_mpart(mail)
    else:
        body = mail.get_payload()
    return body

def getmailheader(header_text, default="ascii"):
    """Decode header_text if needed"""
    try:
        headers=decode_header(header_text)
    except email.Errors.HeaderParseError:
        # This already append in email.base64mime.decode()
        # instead return a sanitized ascii string
        return header_text.encode('ascii', 'replace').decode('ascii')
    else:
        for i, (text, charset) in enumerate(headers):
            try:
                headers[i]=unicode(text, charset or default, errors='replace')
            except LookupError:
                # if the charset is unknown, force default
                headers[i]=unicode(text, default, errors='replace')
        return u"".join(headers)

def getmailaddresses(msg, name):
    """retrieve From:, To: and Cc: addresses"""
    addrs=email.utils.getaddresses(msg.get_all(name, []))
    for i, (name, addr) in enumerate(addrs):
        if not name and addr:
            # only one string! Is it the address or is it the name ?
            # use the same for both and see later
            name=addr
        try:
            # address must be ascii only
            addr=addr.encode('ascii')
        except UnicodeError:
            addr=''
        else:
            # address must match adress regex
            if not email_address_re.match(addr):
                addr=''
        addrs[i]=(getmailheader(name), addr)
    return addrs

def GetMimeMessage(service, user_id, msg_id):
  """Get a Message and use it to create a MIME Message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

  Returns:
    A MIME Message, consisting of data from Message.
  """
  try:
    data = {}
    message = service.users().messages().get(userId='me', id=msg_id,
                                             format='raw').execute(http=auth.getAuth(user_id))

    try:
        msg_str = decode_raw_message(message.get('raw'))
    except ValueError:
        return None
    msg = message_from_string(msg_str)
    subject=getmailheader(msg.get('Subject', ''))
    data["subject"] = subject
    from_ = getmailaddresses(msg, 'from')
    data["from"] = from_
    tos=getmailaddresses(msg, 'to')
    data["to"] = tos
    data['msgId'] = msg_id

    html = []
    text = []
    for part in msg.walk():
        if part.get_content_type() == "text/plain":
            text.append(part)
        elif part.get_content_type() == "text/html":
            html.append(part)
    if html:
        soup = BeautifulSoup(decode_text_payload(html[0]))
        texts = soup.findAll(text=True)
        data["payload"] = "".join(texts)
    elif text:
        data["payload"] = decode_text_payload(text[0])
    else:
        raise Exception('No suitable part found')
    return data

  except errors.HttpError, error:
    print 'An error occurred: %s' % error

class Single(webapp.RequestHandler):
    def get(self):
        self.response.headers.add_header('Content-Type', 'application/json')
        userId = request_user_id(self)
        if userId is None:
            return
        messages = ListMessagesWithLabels(service, userId, None)
        to_me = []
        for msg in messages:
            if rules.message_addressed_to_automation(msg):
                rules.valid_email(msg, userId)
                to_me.append(msg)
        self.response.out.write(json.dumps([], indent = 2, separators=(',', ': ')))

class Handler(webapp.RequestHandler):
    def get(self):
        self.response.headers.add_header('Content-Type', 'application/json')
        userId = request_user_id(self)
        if userId is None:
            return
        messages = ListMessagesWithLabels(service, userId, None)
        self.response.out.write(json.dumps([], indent = 2, separators=(',', ': ')))
