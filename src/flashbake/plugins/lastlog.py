#    Copyright 2022 Ian Paul
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

''' This plugin was inspired by a suggestion from @xtaran on Github.
    It adds information from the lastlog to the commit message. By default this
    includes who logged in to the system in the past 24 hours. That period can
    be modified to suit different needs.'''

from flashbake.plugins import AbstractMessagePlugin
import subprocess
import datetime

class LastLog(AbstractMessagePlugin):
    def __init__(self, plugin_spec):
        AbstractMessagePlugin.__init__(self, plugin_spec)
        self.define_property('period', int, required=False)

    def addcontext(self, message_file, config):
        llog = self.checklog()
        target = ":"
        ''' loop through the lists in the llog variable, and store in the 
        x variable any of the lists that contain a colon.'''
        x = [s for s in llog for i in s if target in i]
        ''' set the period to check the last log to the last 24 hours
        unless the period is set by the user. '''
        if self.period == None:
            self.period = 24
        ''' take the date in each list in variable x, and see if they are equal
        to or newer than the specified period. Then write the relevant log
        entries to the commit message. '''
        message_file.write(f'Most recent lastlog entries: \n')
        for i in x:
            date_placement = [i[3], i[4], i[5], i[6], i[8]]
            y = ' '.join(date_placement)
            past24 = datetime.datetime.now() - datetime.timedelta(hours=self.period)
            if datetime.datetime.strptime(y, "%a %b %d %H:%M:%S %Y") >= past24:
                message_file.write(f'{i[0]} {i[3]} {i[4]} {i[5]} {i[6]} {i[8]}\n')
    def checklog(self):
        ''' Get the lastlog and turn each line of the log into a list. '''
        last = subprocess.run(["lastlog"], capture_output=True,
                text=True).stdout.strip("\n")
        llog = []
        for line in last.splitlines()[1:]:
            x = line.split()
            llog.append(x)
        return llog
        
