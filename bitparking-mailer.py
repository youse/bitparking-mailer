#!/usr/bin/env python2

import urllib2
import json
import smtplib
import os
from datetime import datetime

#  Configuration
USERNAME=""  # bitparking username
THRESHOLD = 75000.0     # notify if your hashrate is less than this value (MH/s)
SERVER="smtp.gmail.com" # e.g.
PORT=587 # e.g.
EMAIL="" # e.g. your_email@gmail.com
EMAIL_PW="" # your email password here

#  Constants
USER_URL='http://mmpool.bitparking.com/userstats/'+USERNAME
ROUND_URL='http://mmpool.bitparking.com/roundstats/'
SENTFILE = ".mailsent"  # tempfile
BLKFILE = ".blocktime"  # file to keep track of block duration
#  key -> (subject, body) mapping for email messages
MESSAGES = {
    'hashdown' : ("HASHRATE DOWN","BAD: reported hashrate is {0}. Investigate immediately!"),
    'hashup' : ("HASHRATE BACK UP :)","GOOD: reported hashrate up to {0}. Good job!"),
    'blockfound' : ("Hooray!  Block found! :)","It only took ~{0}.  Good job!"),
    }

# toggle printing mail status with this decorator
def print_status(fn):
    def fun(self, *args, **kwargs):
        if fn(self, *args, **kwargs):
            print "mail sent",
        else:
            print "mail fail",
    return fun

@print_status
def send_email(key, *args):
    _from = EMAIL
    _to = [EMAIL] #must be a list
    subject = MESSAGES[key][0]
    text = MESSAGES[key][1].format(*args)

    # Prepare actual message
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (_from, ", ".join(_to), subject, text)
    try:
        server = smtplib.SMTP(SERVER, PORT) 
        server.ehlo()
        server.starttls()
        server.login(EMAIL, EMAIL_PW)
        server.sendmail(_from, _to, message)
        #server.quit()
        server.close()
        return True
    except:
        return False

def get_hashrate():
    response = urllib2.urlopen(USER_URL)
    data = json.load(response)
    return data['hashrate']

def get_blocktime():
    response = urllib2.urlopen(ROUND_URL)
    data = json.load(response)
    return data['duration']

class BlockSolveTime(object):
    btzero = '0:0:0'
    btmax = '99999:99:99'

    # HH(HHH):MM:SS to find a block
    def __init__(self, string):
        self.h, self.m, self.s = map(int,string.split(':'))

    def __lt__(self, other):
        if self.h < other.h:
            return True
        elif self.h == other.h:
            if self.m < other.m:
                return True
            elif self.m == other.m:  # 2 blocks in one minute (you never know)
                if self.s < other.s:
                    return True

        return False

    def __str__(self):
        return ":".join(map(lambda a:'{0:02d}'.format(a), [self.h, self.m, self.s]))

    @classmethod
    def load(cls):
        try:
            with open(BLKFILE, 'r') as f:
                data = f.read()
                return cls(data.rstrip())
        except Exception, e:
            print e
            return cls(cls.btzero)

    def dump(self):
        with open(BLKFILE, 'w') as f:
            f.write(str(self))

BST = BlockSolveTime

def hash_notify():
    hashrate = get_hashrate()

    print "Hashrate:",hashrate,"GH/s",
    if hashrate < THRESHOLD:
        print "[Bad]",
        if os.path.exists(SENTFILE):  # we already sent it
            print SENTFILE,"exists, waiting..."
        else:
            print "emailing... ",
            send_email('hashdown', hashrate)
            open(SENTFILE, 'a').close()
    else:
        print "[Good]",
        if os.path.exists(SENTFILE):
            print "emailing... ",
            os.remove(SENTFILE)
            send_email('hashup', hashrate) 
        else:
            pass
            #print "standing pat."

def block_notify():
    old_bt = BST.load()
    new_bt = BST(get_blocktime())
    new_bt.dump()
    #print "Round time:",old_bt,"->",new_bt,

    if new_bt < old_bt:
        print "[New block!] ",
        send_email('blockfound', old_bt)
    else:
        #print "[No new block]",
        pass

if __name__ == '__main__':
    print datetime.now().strftime('%c'),
    hash_notify()
    block_notify()
    print
