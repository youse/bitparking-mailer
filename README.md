bitparking-mailer
=================

Simple python2 script using bitparking's API to send notification emails via an SMTP server.

It's extensible, but mail will currently be sent:
- if your hashrate falls below THRESHOLD
- if a block is solved by the pool

To use, configure your bitparking, mining threshold, and email account information by editing the block at the top of the script.  Email is sent from the given address to itself.

To call, simply (ensuring the script is executable):

`./bitparking-mailer.py`

Here's a crontab entry to run the script every nine minutes (Preferably do this from a different machine than you mine from):

`*/9 * * * *     [username]   cd [script dir] && ./bitparking-mailer.py >> bpmailer.log 2>&1`

I like to then

`tail -f bpmailer.log`

from an SSH session, just to keep tabs on the stats.

==================
say thanks with a satoshi: 1B6ScZT8fLvhQX9YJPYkSBPDRmy8LNyGEi
