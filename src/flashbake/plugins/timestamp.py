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

''' timestamp.py displays the timestamp for a current commit in local or UTC time. '''

from flashbake.plugins import AbstractMessagePlugin
import datetime


class Timestamp(AbstractMessagePlugin):
    def __init__(self, plugin_spec):
        AbstractMessagePlugin.__init__(self, plugin_spec, False)
        self.define_property('time_format', required=False)

    def addcontext(self, message_file, config):

        ''' add a timestamp in local or UTC time '''
        if self.time_format == 'utc':
           message_file.write(str(datetime.datetime.utcnow().strftime('%A, %d %B, %Y %I:%M%p')) + '\n')
        elif self.time_format == 'local':
           message_file.write(str(datetime.datetime.now().strftime('%A, %d %B, %Y %I:%M%p')) + '\n')
        else:
           message_file.write('Time format could not be determined. Please specify utc or local time in your configuration file. \n')

        return True



