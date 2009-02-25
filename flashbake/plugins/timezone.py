#
#  timezone.py
#  Stock plugin to find the system's time zone add to the commit message.

import os, logging
from flashbake.plugins import AbstractMessagePlugin

class TimeZone(AbstractMessagePlugin):
    def init(self, config):
        """ Grab any extra properties that the config parser found and are needed by this module. """
        config.sharedproperty('timezone_tz')

    def addcontext(self, message_file, config):
        """ Add the system's time zone to the commit context. """

        zone = findtimezone(config)

        if zone == None:
            message_file.write('Couldn\'t determine time zone.\n')
        else:
            message_file.write('Current time zone is %s\n' % zone)

        return True

def findtimezone(config):
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
    if 'timezone' in config.__dict__:
        zone = config.timezone
        return zone

    logging.warn('Could not get TZ from env var, /etc/timezone, or .flashbake.')
    zone = None

    return zone
