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

''' This plugin was inspired by a suggestion from @xtaran on GitHub. ''' 
''' It adds information to the commit message about file owners and groups, ''' 
''' and last modified time stamps, for files in the project directory. '''

from flashbake.plugins import AbstractMessagePlugin
import subprocess
import os

class FileOwners(AbstractMessagePlugin):
    def __init__(self, plugin_spec):
        AbstractMessagePlugin.__init__(self, plugin_spec)
        self.define_property('owners', required=False) 
        # Adds owner, group, and last modified time stamp to the commit message
        #for each file in the specified directory. 

    def addcontext(self, message_file, config):
        if self.owners == None:
            try:
                self.owners = os.getcwd()
            except:
                message_file.write('Couldn\'t find the specified directory. Please ensure the config uses an absolute path. \n')
                return False

        ''' Add owners and groups data for the files and folders '''
        ''' in the current directory. '''
        fields = self.__getowners(self.owners)
        for i in range(len(fields)):
            message_file.write("{0} {1} {2} {3} {4}\n".format(fields[i][2], 
                fields[i][3], fields[i][5], fields[i][6], fields[i][7]))

    def __getowners(self, owners):
        check = subprocess.run(["ls", "-lAt", "--time-style=long-iso", owners],
                capture_output=True, text=True).stdout.strip("\n")
        fields = []
        for line in check.splitlines()[1:]:
            x = line.split()
            fields.append(x)
        return fields 

