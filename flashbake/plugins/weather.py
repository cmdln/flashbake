#
#  weather.py
#  Stock plugin for adding weather information to context, must have TZ or
#  /etc/localtime available to determine city from ISO ID.

import sys
import urllib, urllib2
import xml.dom.minidom
import os
import os.path
import string
import logging
from urllib2 import HTTPError, URLError
from flashbake.context import findtimezone, parsecity

connectable = True

def init(control_config):
    """ Grab any extra properties that the config parser found and are needed by this module. """

def addcontext(message_file, control_config):
    """ Add weather information, based in the TZ, to the commit message. """
    zone = findtimezone(control_config)
    if None == zone:
        message_file.write('Couldn\'t fetch current weather.\n')
        return False

    city = parsecity(zone)

    # call the Google weather API with the city
    weather = getweather(city)

    if len(weather) > 0:
        # there is also an entry for the key, wind_condition, in the weather
        # dictionary
        message_file.write('Current weather is %(condition)s (%(temp_f)sF/%(temp_c)sC) %(humidity)s\n'\
                % weather)
    else:
        message_file.write('Couldn\'t fetch current weather.\n')
    return len(weather) > 0

def getweather(city):
    """ This relies on Google's unpublished weather API which may change without notice. """

    # unpublished API that iGoogle uses for its weather widget
    baseurl = 'http://www.google.com/ig/api?'
    # encode the sole paramtere
    for_city = baseurl + urllib.urlencode({'weather': city})

    # necessary machinery to fetch a web page
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())

    try:
        logging.debug('Requesting page for %s.' % for_city)

        # open the weather API page
        weather_xml = opener.open(urllib2.Request(for_city)).read()

        # the weather API returns some nice, parsable XML
        weather_dom = xml.dom.minidom.parseString(weather_xml)

        # just interested in the conditions at the moment
        current = weather_dom.getElementsByTagName("current_conditions")

        weather = {}
        for child in current[0].childNodes:
           if child.localName == 'icon':
               continue
           weather[child.localName] = child.getAttribute('data').strip()

        return weather
    except HTTPError, e:
        logging.error('Failed with HTTP status code %d' % e.code)
        return {}
    except URLError, e:
        logging.error('Failed with reason %s.' % e.reason)
        return {}
