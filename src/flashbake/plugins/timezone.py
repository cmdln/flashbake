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


'''  timezone.py - Stock plugin to find the system's time zone add to the commit message.'''

from flashbake.plugins import AbstractMessagePlugin
import logging
import os



PLUGIN_SPEC = 'flashbake.plugins.timezone:TimeZone'

class TimeZone(AbstractMessagePlugin):
    def __init__(self, plugin_spec):
        AbstractMessagePlugin.__init__(self, plugin_spec, False)
        self.share_property('tz', plugin_spec=PLUGIN_SPEC)

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
