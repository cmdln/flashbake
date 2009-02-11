#
#  context.py
#  Build up some descriptive context for automatic commit to git

import sys
import urllib, urllib2
import xml.dom.minidom
import os
import os.path
import string
import random

class ControlConfig:
    """
    Gather control options parsed out of the dot-control file in a project.
    """

    def __init__(self):
        self.feed = None
        self.limit = 3
        self.author = None
        self.email = None
        self.notice_to = None
        self.notice_from = None
        self.smtp_port = 25
        self.int_props = ('limit', 'smtp_port')
        self.plugins = list()

    def capture(self, line):
        # grab comments but don't do anything
        if line.startswith('#'):
            return True

        # grab blanks but don't do anything
        if len(line.strip()) == 0:
            return True

        if line.find(':') > 0:
            prop_tokens = line.split(':', 1)
            prop_name = prop_tokens[0].strip()
            prop_value = prop_tokens[1].strip()

            if 'plugins' == prop_name:
               self.initplugins(prop_value.split(','))
               return True

            # only capture explicitly initialized attributes
            if not prop_name in self.__dict__:
                print 'Ignoring unkown property, %s' % prop_name
                return True

            if prop_name in self.int_props:
                prop_value = int(prop_value)
            self.__dict__[prop_name] = prop_value

            return True

        return False

    def fix(self):
        """
        Do any property clean up, after parsing but before use
        """

        if self.notice_from == None and self.notice_to != None:
            self.notice_from = self.notice_to

        if len(self.plugins) == 0:
            self.initplugins(('flashbake.plugins.timezone',
                    'flashbake.plugins.weather',
                    'flashbake.plugins.uptime',
                    'flashbake.plugins.feed'))

        if self.feed == None or self.author == None or self.notice_to == None:
            print 'Make sure that feed:, author:, and notice_to: are in the .control file'
            sys.exit(1)

    def initplugins(self, plugin_names):
        for plugin_name in plugin_names:
            __import__(plugin_name)
            plugin_module = sys.modules[plugin_name]
            self.plugins.append(plugin_module)

def calcuptime():
    """ copied with blanket permission from
        http://thesmithfam.org/blog/2005/11/19/python-uptime-script/ """

    try:
         f = open( "/proc/uptime" )
         contents = f.read().split()
         f.close()
    except:
        return None

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

def buildmessagefile(control_config):
    """ Build a commit message that uses the provided ControlConfig object and
        return a reference to the resulting file. """

    zone = findtimezone()
    city = parsecity(zone)

    # with thanks to Dave Smith
    uptime = calcuptime()
    
    msg_filename = '/tmp/git_msg_%d' % random.randint(0,1000)

    # try to avoid clobbering another process running this script
    while os.path.exists(msg_filename):
        msg_filename = '/tmp/git_msg_%d' % random.randint(0,1000)

    connected = False

    message_file = open(msg_filename, 'w')
    try:
        for plugin in control_config.plugins:
            plugin_success = plugin.addcontext(message_file, control_config)
            # TODO track this only for connected plugins
            connected = connected or plugin_success
        if not connected:
            message_file.write('System is most likely offline.')
    finally:
        message_file.close()
    return msg_filename

def findtimezone():
    # check the environment for the zone value
    zone = os.environ.get("TZ")

    # some desktops don't set the env var but /etc/timezone should
    # have the value regardless
    if None == zone:
        if not os.path.exists('/etc/timezone'):
            print 'Could not get TZ from env var or /etc/timezone.'
            zone = None
        else:
            zone_file = open('/etc/timezone')
            zone = zone_file.read()
            zone = zone.replace("\n", "")
    return zone

def parsecity(zone):
    tokens = zone.split("/")
    if len(tokens) != 2:
        print 'Zone id, "', zone, '", doesn''t appear to contain a city.'
        # return non-zero so calling shell script can catch
        return None

    city = tokens[1]
    # ISO id's have underscores, convert to spaces for the Google API
    return city.replace("_", " ")
