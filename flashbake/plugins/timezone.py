#
#  timezone.py
#  Stock plugin to find the system's time zone add to the commit message.

import os, logging, urllib, urllib2, xml
from urllib2 import HTTPError, URLError
from flashbake.plugins import AbstractMessagePlugin

class TimeZone(AbstractMessagePlugin):
    def init(self, config):
        """ Grab any extra properties that the config parser found and are needed by this module. """
        config.sharedproperty('timezone_tz')
        config.sharedproperty('location_data')

    def addcontext(self, message_file, config):
        """ Add the system's time zone to the commit context. """

        zone = findtimezone(config)

        if zone == None:
            message_file.write('Couldn\'t determine time zone.\n')
        else:
            message_file.write('Current time zone is %s\n' % zone)

        return True

## TODO: add caching
def __findtimezone_from_location(config):
    zone = None
    # check for location_data
    if False:
    #if config.location_data != None:
        base_url = 'http://ws.geonames.org/timezone?'
        for_tz = base_url + urllib.urlencode({
            'lat': config.location_data.get('Latitude',''),
            'lng': config.location_data.get('Longitude','')
            })
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())

        try:
            logging.debug('Requesting page for %s.' % for_tz)

            # open the TZ API page
            location_xml = opener.open(urllib2.Request(for_tz)).read()
            location_dom = xml.dom.minidom.parseString(location_xml)
            response = location_dom.getElementsByTagName("timezoneId")
            if (len(response) > 0):
                zone = response[0]
        except HTTPError, e:
            logging.error('Failed with HTTP status code %d' % e.code)
            pass
        except URLError, e:
            logging.error('Failed with reason %s.' % e.reason)
            pass

    return zone

def findtimezone(config):

    zone = __findtimezone_from_location(config)
    if None != zone:
        logging.debug('Returning timezone based on location data: %s' % zone)
        return zone
    
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
