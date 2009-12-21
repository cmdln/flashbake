#    copyright 2009 Thomas Gideon
#
#    This file is part of flashbake.
#
#    flashbake is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    flashbake is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with flashbake.  If not, see <http://www.gnu.org/licenses/>.

'''  uptime.py - Stock plugin to calculate the system's uptime and add to the commit message.'''

from flashbake.plugins import AbstractMessagePlugin
from subprocess import Popen, PIPE
import flashbake
import logging
import os.path



class UpTime(AbstractMessagePlugin):
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
            return self.__run_uptime()

        f = open("/proc/uptime")
        try:
            contents = f.read().split()
        except:
            return None
        finally:
            f.close()

        total_seconds = float(contents[0])

        # Helper vars:
        MINUTE = 60
        HOUR = MINUTE * 60
        DAY = HOUR * 24

        # Get the days, hours, etc:
        days = int(total_seconds / DAY)
        hours = int((total_seconds % DAY) / HOUR)
        minutes = int((total_seconds % HOUR) / MINUTE)
        seconds = int(total_seconds % MINUTE)

        # Build up the pretty string (like this: "N days, N hours, N minutes, N seconds")
        string = ""
        if days > 0:
            string += str(days) + " " + (days == 1 and "day" or "days") + ", "
        if len(string) > 0 or hours > 0:
            string += str(hours) + " " + (hours == 1 and "hour" or "hours") + ", "
        if len(string) > 0 or minutes > 0:
            string += str(minutes) + " " + (minutes == 1 and "minute" or "minutes") + ", "
        string += str(seconds) + " " + (seconds == 1 and "second" or "seconds")

        return string

    def __run_uptime(self):
        """ For OSes that don't provide procfs, then try to use the updtime command.
        
            Thanks to Tony Giunta for this contribution. """
        if not flashbake.executable_available('uptime'):
            return None

        # Try to capture output of 'uptime' command, 
        # if not found, catch OSError, log and return None
        try:
            output = Popen("uptime", stdout=PIPE).communicate()[0].split()
        except OSError:
            logging.warn("Can't find 'uptime' command in $PATH")
            return None

        # Parse uptime output string
        # if len == 10 or 11, uptime is less than a day
        if len(output) in [10, 11]:
            days = "00"
            hours_and_minutes = output[2].strip(",")
        elif len(output) == 12:
            days = output[2]
            hours_and_minutes = output[4].strip(",")
        else:
            return None

        # If time is exactly x hours/mins, no ":" in "hours_and_minutes" 
        # and the interpreter will throw a ValueError
        try:
            hours, minutes = hours_and_minutes.split(":")
        except ValueError:
            if output[3].startswith("hr"):
                hours = hours_and_minutes
                minutes = "00"
            elif output[3].startwwith("min"):
                hours = "00"
                minutes = hours_and_minutes
            else:
                return None

        # Build up output string, might require Python 2.5+
        uptime = (days + (" day, " if days == "1" else " days, ") + 
                hours + (" hour, " if hours == "1" else " hours, ") + 
                minutes + (" minute" if minutes == "1" else " minutes"))

        return uptime

