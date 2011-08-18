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

'''  weather.py - Stock plugin for adding weather information to context, must have TZ or
 /etc/localtime available to determine city from ISO ID. '''

from flashbake.plugins import AbstractMessagePlugin
from flashbake.plugins.timezone import findtimezone
from urllib2 import HTTPError, URLError
import logging
import re
import timezone
import urllib
import urllib2
import xml.dom.minidom



class Weather(AbstractMessagePlugin):
    def __init__(self, plugin_spec):
        AbstractMessagePlugin.__init__(self, plugin_spec, True)
        self.define_property('city')
        self.share_property('tz', plugin_spec=timezone.PLUGIN_SPEC)
        ## plugin uses location_location from Location plugin
        self.share_property('location_location')

    def addcontext(self, message_file, config):
        """ Add weather information to the commit message. Looks for
            weather_city: first in the config information but if that is not
            set, will try to use the system time zone to identify a city. """
        if config.location_location == None and self.city == None:
            zone = findtimezone(config)
            if zone == None:
                city = None
            else:
                city = self.__parsecity(zone)
        else:
            if config.location_location == None:
                city = self.city
            else:
                city = config.location_location

        if None == city:
            message_file.write('Couldn\'t determine city to fetch weather.\n')
            return False

        # call the Google weather API with the city
        weather = self.__getweather(city)

        if len(weather) > 0:
            # there is also an entry for the key, wind_condition, in the weather
            # dictionary
            message_file.write('Current weather for %(city)s is %(condition)s (%(temp_f)sF/%(temp_c)sC) %(humidity)s\n'\
                    % weather)
        else:
            message_file.write('Couldn\'t fetch current weather for city, %s.\n' % city)
        return len(weather) > 0

    def __getweather(self, city):
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
            request = opener.open(urllib2.Request(for_city, headers={'Accept-Charset': 'UTF-8'}))
            weather_xml = request.read()
            # figure out whether the response is other than utf-8 and decode if needed
            if 'Content-Type' in request.info():
                content_type = request.info()['Content-Type']
                charset_m = re.search('.*; charset=(.*)$', content_type)
                if charset_m is not None:
                    req_charset = charset_m.group(1)
                    logging.debug('Decoding using charset, %s, based on the response.' % req_charset)
                    weather_xml = weather_xml.decode(req_charset)

            # the weather API returns some nice, parsable XML
            weather_dom = xml.dom.minidom.parseString(weather_xml.encode('utf8'))

            # just interested in the conditions at the moment
            current = weather_dom.getElementsByTagName("current_conditions")

            if current == None or len(current) == 0:
                return dict()

            weather = dict()
            weather['city'] = city
            for child in current[0].childNodes:
                if child.localName == 'icon':
                    continue
                weather[child.localName] = child.getAttribute('data').strip()

            return weather
        except HTTPError, e:
            logging.error('Failed with HTTP status code %d' % e.code)
            return {}
        except URLError, e:
            logging.error('Plugin, %s, failed to connect with network.' % self.__class__)
            logging.debug('Network failure reason, %s.' % e.reason)
            return {}

    def __parsecity(self, zone):
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
