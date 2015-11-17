import send
import random
from google.appengine.api import memcache

# set email address of user
email_address = "youremail@youremail.com"

# these are approved users
from_users = ['approveduser@approveduser.com']

buzz_map = [
    {"keyword": "gareth", "response": "Looks like you were emailing regarding Gareth. He loves coffee, you should consider buying him one"}
]

cheeky = ["Thanks for your note. This reply is being generated from a robot. \n\n",
          "Thanks for reaching out. I'd love to say I wrote this message, but the contents below is being generated by a robot. \n\n",
          "Hi,\n\nGreat message. Unfortunately it's just me here right now, this is Ronald (an automated robot). \n\n",
          "Hey,\n\nThanks for the message. This is Ronald the Robot, stepping in.\n\n",
          "Greetings!\n\nThis is Ronald The Robot. \n\n",
          "Hi,\n\nThis is Ronald (the robot) stepping in. \n\n",
          "Hi,\n\nThanks for your note. This is Ronald the robot. \n\n"]

unknown = ["Wow complicated email. I'm working on a reply, if this is urgent please feel free to dial 911.\n\n",
           "This is perplexingly difficult, but I couldn't parse your email. Let me go and grab a coffee. I'll be back soon..\n\n",
           "This is awkward. I couldn't quite parse your email to understand what this email is about. Let me get back to you soon\n\n",
           "Eeek, I couldn't figure out what your email is about. Let me get back to you as soon as I can.. (#robotfailure)\n\n"]

ending = ["Best,\nRonald The Robot\n", "Cheers,\nYour Cheeky Robot (Ronald)", "Thanks,\nRonald", "Thanks,\n Ronald The Robot", "Thanks,\nRonald\n\np.s. if you know how I can get out of here please reply.."]

def check_map(words):
    resp = ""
    for word in words:
        for buzz_word in buzz_map:
            if buzz_word['keyword'].lower() == word.lower():
                resp = buzz_word['response']
    if resp == "":
        resp = random.choice(unknown)

    return random.choice(cheeky) + resp + "\n\n" + random.choice(ending)

def parse_email(txt):
    #todo strip all common words from email
    all_words = txt.split()
    return check_map(all_words)

def cache_check(msgId):
    data = memcache.get("msg_" + msgId)
    if data is not None:
        return False
    else:
        return True

def valid_email(msg, user_id):
    print "validation check"
    _from = msg['from']
    for user in _from:
        if user[1] in from_users:
            msgId = msg['msgId']
            if cache_check(msgId):
                sendEmail(user_id, user[1], "Re: " + msg['subject'] + "", parse_email(msg['payload']))
                memcache.add("msg_" + msgId, msgId)

def sendEmail(user_id, to, subject, msg):
    # if not in cache
    # do cache check for sent email messages
    send.SendMessage(user_id, send.CreateMessage(email_address, to, subject, msg))
