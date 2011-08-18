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
#
# the iTunes class is based on the itunes.py by Andrew Wheiss, originally
# licensed under an MIT License

'''  music.py - Plugin for gathering last played tracks from music player. '''

from flashbake.plugins import AbstractMessagePlugin
import flashbake
import logging
import os.path
import sqlite3
import subprocess
import time



class Banshee(AbstractMessagePlugin):
    def __init__(self, plugin_spec):
        """ Add an optional property for specifying a different location for the
            Banshee database. """
        AbstractMessagePlugin.__init__(self, plugin_spec)
        self.define_property('db', default=os.path.join(os.path.expanduser('~'), '.config', 'banshee-1', 'banshee.db'))
        self.define_property('limit', int, default=3)
        self.define_property('last_played_format')

    def addcontext(self, message_file, config):
        """ Open the Banshee database and query for the last played tracks. """
        query = """\
select t.Title, a.Name, t.LastPlayedStamp
from CoreTracks t
join CoreArtists a on t.ArtistID = a.ArtistID
order by LastPlayedStamp desc
limit %d"""
        query = query.strip() % self.limit
        conn = sqlite3.connect(self.db)
        try:
            cursor = conn.cursor()
            logging.debug('Executing %s' % query)
            cursor.execute(query)
            results = cursor.fetchall()
            message_file.write('Last %d track(s) played in Banshee:\n' % len(results))
            for result in results:
                last_played = time.localtime(result[2])
                if self.last_played_format != None:
                    logging.debug('Using format %s' % self.last_played_format)
                    last_played = time.strftime(self.last_played_format,
                            last_played)
                else:
                    last_played = time.ctime(result[2])
                message_file.write('"%s", by %s (%s)' %
                        (result[0], result[1], last_played))
                message_file.write('\n')
        except Exception, error:
            logging.error(error)
            conn.close()

        return True


class iTunes(AbstractMessagePlugin):
    ''' Based on Andrew Heiss' plugin which is MIT licensed which should be compatible. '''
    def __init__(self, plugin_spec):
        AbstractMessagePlugin.__init__(self, plugin_spec)
        self.define_property('osascript')
        
    def init(self, config):
        if self.osascript is None:
            self.osascript = flashbake.find_executable('osascript')

    def addcontext(self, message_file, config):
        """ Get the track info and write it to the commit message """

        info = self.trackinfo()

        if info is None:
            message_file.write('Couldn\'t get current track.\n')
        else:
            message_file.write('Currently playing in iTunes:\n%s' % info)

        return True

    def trackinfo(self):
        ''' Call the AppleScript file. '''
        if self.osascript is None:
            return None
        directory = os.path.dirname(__file__)
        script_path = os.path.join(directory, 'current_track.scpt')

        args = [self.osascript, script_path]
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             close_fds=True)

        return proc.communicate()[0]
