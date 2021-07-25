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
import urllib.request
from urllib.parse import urlencode
import json
import logging

PLUGIN_SPEC = 'flashbake.plugins.weather:Weather'



class Weather(AbstractMessagePlugin):
    def __init__(self, plugin_spec):
        AbstractMessagePlugin.__init__(self, plugin_spec, True)
        self.define_property('city')
        self.define_property('units', required=False, default='imperial')
        self.define_property('appid', required=False)
        self.share_property('tz', plugin_spec=timezone.PLUGIN_SPEC)
        ## plugin uses location_location from Location plugin
        self.share_property('location_location')

    def addcontext(self, message_file, config):
        """ Add weather information to the commit message. Looks for
            weather_city: first in the config information but if that is not
            set, will try to use the system time zone to identify a city. """
        if self.city == None:
            message_file.write('Couldn\'t determine city to fetch weather.\n')
            return False

        if self.appid == None:
            message_file.write('Open Weather Map requires an API key. For more information see: https://github.com/commandline/flashbake/wiki/Plugins')
            return False

        # call the open weather map API with the city
        weather = self.__getweather(self.city, self.appid, self.units)

        if len(weather) > 0:
            message_file.write("Current weather for {city}: {description}, {temp}\u00b0{temp_units}, {humidity}% humidity\n".format_map(weather))
        else:
            message_file.write('Couldn\'t fetch current weather for city, {}.\n'.format(self.city))
        return len(weather) > 0

    def __getweather(self, city, appid, units='imperial'):
        """ This relies on Open Weather Map's API which may change without notice. """

        baseurl = 'https://api.openweathermap.org/data/2.5/weather?'
        # encode the parameters
        params = {'q': city, 'units': units, 'appid': appid}
        for_city = baseurl + urlencode(params)
 
        try:
            logging.debug('Requesting page for {}.'.format(for_city))
            
            # Get the json-encoded string
            raw = urllib.request.Request(for_city)
            with urllib.request.urlopen(raw) as response:
                the_page = response.read()
        
            # Convert it to something usable
            data = json.loads(the_page)

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
        except urllib.error.HTTPError as e:
            logging.error(f'Failed with HTTP status code {e.code}')
            return {}
        except urllib.error.URLError as e:
            logging.error('Plugin, {}, failed to connect with network.'.format(self.__class__))
            logging.debug('Network failure reason, {}.'.format(e.reason))
            return {}

    def __parsecity(self, zone):
        if None == zone:
            return None
        tokens = zone.split("/")
        if len(tokens) != 2:
            logging.warning('Zone id, "{}", doesn''t appear to contain a city.'.format(zone))
            # return non-zero so calling shell script can catch
            return None

        city = tokens[1]
        # ISO id's have underscores, convert to spaces for the Google API
        return city.replace("_", " ")
