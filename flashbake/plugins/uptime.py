#
#  uptime.py
#  Stock plugin to calculate the system's uptime and add to the commit message.

import string
import os.path
import logging
from flashbake.plugins import AbstractMessagePlugin

class UpTime(AbstractMessagePlugin):
    def init(self, config):
        """ Nothing needed. """

    def addcontext(self, message_file, config):
        """ Add the system's up time to the commit context. """

        uptime = self.__calcuptime()

        if uptime == None:
            message_file.write('Couldn\'t determine up time.\n')
        else:
            message_file.write('System has been up %s\n' % uptime)

        return True

    def __calcuptime(self):
        """ copied with blanket permission from
            http://thesmithfam.org/blog/2005/11/19/python-uptime-script/ """

        if not os.path.exists('/proc/uptime'):
            logging.warn('/proc/uptime doesn\'t exist.')
            return None

        f = open( "/proc/uptime" )
        try:
             contents = f.read().split()
        except:
            return None
        finally:
             f.close()

        total_seconds = float(contents[0])

        # Helper vars:
        MINUTE  = 60
        HOUR    = MINUTE * 60
        DAY     = HOUR * 24

        # Get the days, hours, etc:
        days    = int( total_seconds / DAY )
        hours   = int( ( total_seconds % DAY ) / HOUR )
        minutes = int( ( total_seconds % HOUR ) / MINUTE )
        seconds = int( total_seconds % MINUTE )

        # Build up the pretty string (like this: "N days, N hours, N minutes, N seconds")
        string = ""
        if days> 0:
            string += str(days) + " " + (days == 1 and "day" or "days" ) + ", "
        if len(string)> 0 or hours> 0:
            string += str(hours) + " " + (hours == 1 and "hour" or "hours" ) + ", "
        if len(string)> 0 or minutes> 0:
            string += str(minutes) + " " + (minutes == 1 and "minute" or "minutes" ) + ", "
        string += str(seconds) + " " + (seconds == 1 and "second" or "seconds" )

        return string
