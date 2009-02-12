#
#  context.py
#  Build up some descriptive context for automatic commit to git

import sys
import os
import os.path
import string
import random
import logging

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
                logging.debug('Ignoring unkown property, %s' % prop_name)
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
            logging.debug('No plugins configured, enabling the stock set.')
            self.initplugins(('flashbake.plugins.timezone',
                    'flashbake.plugins.weather',
                    'flashbake.plugins.uptime',
                    'flashbake.plugins.feed'))

        if self.feed == None or self.author == None or self.notice_to == None:
            logging.error('Make sure that feed:, author:, and notice_to: are in the .control file')
            sys.exit(1)

    def initplugins(self, plugin_names):
        for plugin_name in plugin_names:
            try:
                __import__(plugin_name)
            except ImportError:
                logging.warn('Invalid module, %1s' % plugin_name)
                continue

            plugin_module = sys.modules[plugin_name]

            if plugin_module.addcontext == None:
                logging.warn('Plugin, %s, doesn\' provide the addcontext function.' % plugin_name)
                continue

            self.plugins.append(plugin_module)

def buildmessagefile(control_config):
    """ Build a commit message that uses the provided ControlConfig object and
        return a reference to the resulting file. """

    msg_filename = '/tmp/git_msg_%d' % random.randint(0,1000)

    # try to avoid clobbering another process running this script
    while os.path.exists(msg_filename):
        msg_filename = '/tmp/git_msg_%d' % random.randint(0,1000)

    connected = False

    message_file = open(msg_filename, 'w')
    try:
        for plugin in control_config.plugins:
            plugin_success = plugin.addcontext(message_file, control_config)
            # let each plugin say which ones attempt network connections
            if plugin.connectable:
                connected = connected or plugin_success
        if not connected:
            message_file.write('System is most likely offline.')
    finally:
        message_file.close()
    return msg_filename

def findtimezone():
    # check the environment for the zone value
    zone = os.environ.get("TZ")

    logging.debug('Zone from env is %s.' % zone)

    # some desktops don't set the env var but /etc/timezone should
    # have the value regardless
    if None == zone:
        if not os.path.exists('/etc/timezone'):
            logging.warn('Could not get TZ from env var or /etc/timezone.')
            return None
        zone_file = open('/etc/timezone')

        try:
            zone = zone_file.read()
        finally:
            zone_file.close()
        zone = zone.replace("\n", "")

    return zone

def parsecity(zone):
    if None == zone:
        return None
    tokens = zone.split("/")
    if len(tokens) != 2:
        logging.warning('Zone id, "%s", doesn''t appear to contain a city.' % zone)
        # return non-zero so calling shell script can catch
        return None

    city = tokens[1]
    # ISO id's have underscores, convert to spaces for the Google API
    return city.replace("_", " ")
