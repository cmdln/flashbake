#    copyright 2009 Thomas Gideon
#    Modified 2013 Bryan Fordham <bfordham@gmail.com>
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
from flashbake.plugins import timezone
from urllib2 import HTTPError, URLError
import json
import logging
import re
import urllib
import urllib2



class Weather(AbstractMessagePlugin):
    def __init__(self, plugin_spec):
        AbstractMessagePlugin.__init__(self, plugin_spec, True)
        self.define_property('city')
        self.define_property('units', required=False, default='imperial')
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

        # call the open weather map API with the city
        weather = self.__getweather(city, self.units)

        if len(weather) > 0:
            message_file.write('Current weather for %(city)s: %(description)s. %(temp)i%(temp_units)s. %(humidity)s%% humidity\n'
                    % weather)
        else:
            message_file.write('Couldn\'t fetch current weather for city, %s.\n' % city)
        return len(weather) > 0

    def __getweather(self, city, units='imperial'):
        """ This relies on Open Weather Map's API which may change without notice. """

        baseurl = 'http://api.openweathermap.org/data/2.5/weather?'
        # encode the parameters
        for_city = baseurl + urllib.urlencode({'q': city, 'units': units})

        try:
            logging.debug('Requesting page for %s.' % for_city)
            
            # Get the json-encoded string
            raw = urllib2.urlopen(for_city).read()
        
            # Convert it to something usable
            data = json.loads(raw)

            # Grab the information we want
            weather = dict()
            
            for k,v in (data['weather'][0]).items():
              weather[k] = v

            for k,v in data['main'].items():
              weather[k] = v

            weather['city'] = city
            
            if units == 'imperial':
              weather['temp_units'] = 'F'
            elif units == 'metric':
              weather['temp_units'] = 'C'
            else:
              weather['temp_units'] = 'K'

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
