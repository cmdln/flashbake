#  location.py
#  Net location plugin.

import logging
import urllib2
import re
from urllib2 import HTTPError, URLError
from flashbake.plugins import AbstractMessagePlugin

class Location(AbstractMessagePlugin):
    def addcontext(self, message_file, config):
        # unpublished API that iGoogle uses for its weather widget
        no_reply = 'http://www.noreply.org'
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())

        try:
            # open the weather API page
            ping_reply = opener.open(urllib2.Request(no_reply)).read()
            hello_line = None
            for line in ping_reply.split('\n'):
                if line.find('Hello') > 0:
                    hello_line = line.strip()
                    break
            if hello_line == None:
                message_file.write('Failed to parse Hello with public IP address.')
            logging.debug(hello_line)
            m = re.search('([0-9]+\.){3}([0-9]+){1}', hello_line)
            if m == None:
                message_file.write('Failed to parse Hello with public IP address.')
            ip_addr = m.group(0)
            logging.debug(ip_addr)
            return True
        except HTTPError, e:
            logging.error('Failed with HTTP status code %d' % e.code)
            message_file.write('Failed to get public IP for geo location.\n')
            return False
        except URLError, e:
            logging.error('Failed with reason %s.' % e.reason)
            message_file.write('Failed to get public IP for geo location.\n')
            return False
