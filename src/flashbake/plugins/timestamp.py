#    Copyright 2017 Ian Paul
#    Copyright 2009 Thomas Gideon
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

''' timestamp.py displays the timestamp for a current commit in local or UTC time using a 12- or 24-hour clock.
    thanks to @carlosalonso (on GitHub) for the suggestion. '''

from flashbake.plugins import AbstractMessagePlugin
from flashbake.plugins.timezone import findtimezone 
import datetime


class Timestamp(AbstractMessagePlugin):
    def __init__(self, plugin_spec):
        AbstractMessagePlugin.__init__(self, plugin_spec, False)
        self.define_property('time_format', required=False)
        self.define_property('time_hours', required=False)

    def addcontext(self, message_file, config):

        ''' Determine whether the timestamp is in local or UTC time, and whether it uses a 12- or 24-hour clock. '''

        if self.time_format.casefold() == 'UTC' and self.time_hours == '24':
           zone = findtimezone(config)
           message_file.write(str(datetime.datetime.utcnow().strftime('%A, %B %d, %Y %H:%M UTC in ') + str(zone) + '\n'))
        elif self.time_format.casefold() == 'UTC' and self.time_hours == '12':
           zone = findtimezone(config)
           message_file.write(str(datetime.datetime.utcnow().strftime('%A, %B %d, %Y %I:%M %p UTC in ') + str(zone) + '\n'))
        elif self.time_format.casefold() == 'local' and self.time_hours == '24':
           zone = findtimezone(config)
           message_file.write(str(datetime.datetime.now().strftime('%A, %B %d, %Y %H:%M in ') + str(zone) + '\n'))
        elif self.time_format.casefold() == 'local' and self.time_hours == '12':
           zone = findtimezone(config)
           message_file.write(str(datetime.datetime.now().strftime('%A, %B %d, %Y %I:%M %p in ') + str(zone) + '\n'))
        else:
           message_file.write('Time format could not be determined. Please specify UTC or local time, and a 12- or 24-hour clock in your configuration file. \n')
