#
#  context.py
#  Build up some descriptive context for automatic commit to git

import sys
import os
import os.path
import string
import random
import logging

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
            message_file.write('All of the plugins that use the network failed.\n')
            message_file.write('Your computer may not be connected to the network.')
    finally:
        message_file.close()
    return msg_filename

def findtimezone(control_config):
    # check the environment for the zone value
    zone = os.environ.get("TZ")

    logging.debug('Zone from env is %s.' % zone)

    # some desktops don't set the env var but /etc/timezone should
    # have the value regardless
    if None != zone:
        logging.debug('Returning env var value.')
        return zone

    # this is common on many *nix variatns
    logging.debug('Checking /etc/timezone')
    if os.path.exists('/etc/timezone'):
        zone_file = open('/etc/timezone')

        try:
            zone = zone_file.read()
        finally:
            zone_file.close()
        zone = zone.replace("\n", "")
        return zone

    # this is specific to OS X
    logging.debug('Checking /etc/localtime')
    if os.path.exists('/etc/localtime'):
        zone = os.path.realpath('/etc/localtime')
        (zone, city) = os.path.split(zone);
        (zone, continent) = os.path.split(zone);
        zone = os.path.join(continent, city)
        return zone

    logging.debug('Checking .flashbake')
    if 'timezone' in control_config.__dict__:
        zone = control_config.timezone
        return zone

    logging.warn('Could not get TZ from env var, /etc/timezone, or .flashbake.')
    zone = None

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
