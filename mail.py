#
#  commit-wrapper.py
#  Parses a project's control file and wraps git operations, calling the context
#  script to build automatic commit messages as needed.
#
#  Created by Thomas Gideon (cmdln@thecommandline.net) on 1/25/2009
#  Provided as-is, with no warranties
#  License: http://creativecommons.org/licenses/by-nc-sa/3.0/us/ 

import os
import sys
# Import smtplib for the actual sending function
import smtplib
# Import the email modules we'll need
from email.mime.text import MIMEText


def send_orphans(notice_to, notice_from):
    body = 'Fooby dooby'
    
    # Create a text/plain message
    msg = MIMEText(body, 'plain')

    msg['Subject'] = 'Foo subject'
    msg['From'] = notice_from
    msg['To'] = notice_to

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP(port=25)
    s.connect()
    print 'Sending notice to %s.' % notice_to
    s.sendmail(notice_from, [notice_to], msg.as_string())
    s.close()

# call go() when this module is executed as the main script
if __name__ == "__main__":
    send_orphans('cmdln@thecommandline.net', 'cmdln@localhost')
