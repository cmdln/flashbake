#    copyright 2009 Thomas Gideon
#    Modified 2021 Ian Paul
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
#    The Music class is based on itunes.py by Andrew Heiss, originally
#    licensed under an MIT License
#
#    The Rhythmbox class was created by Ian Paul and is distirubted under
#    the same general license as flashbake

'''  music.py - Plugin for gathering last played tracks from music player. '''

from flashbake.plugins import AbstractMessagePlugin
import flashbake
import logging
import os.path
import subprocess
import time
import datetime
import xml.etree.ElementTree as ET

class Music(AbstractMessagePlugin):
    ''' Based on Andrew Heiss' plugin which is MIT licensed which should be compatible. '''
    def __init__(self, plugin_spec):
        AbstractMessagePlugin.__init__(self, plugin_spec)
        self.define_property('osascript')
        
    def init(self, config):
        if self.osascript is None:
            self.osascript = flashbake.find_executable('osascript')

    def addcontext(self, message_file, config):
        """ Get the track info and write it to the commit message """

        info = self.trackinfo().decode('utf-8')

        if info is None:
            message_file.write('Couldn\'t get current track.\n')
        else:
            message_file.write(f'Currently playing in Music:\n{info}')

        return True

    def trackinfo(self):
        ''' Call the AppleScript file. '''
        if self.osascript is None:
            return None
        directory = os.path.dirname(__file__)
        script_path = os.path.join(os.path.expanduser('~'), 'Documents', 'current_track.scpt')

        args = [self.osascript, script_path]
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             close_fds=True)

        return proc.communicate()[0]

class Rhythmbox(AbstractMessagePlugin):
    def __init__(self, plugin_spec):
        AbstractMessagePlugin.__init__(self, plugin_spec)
        self.define_property('db', default=os.path.join(os.path.expanduser('~'), '.local', 'share', 'rhythmbox', 'rhythmdb.xml'))

    def addcontext(self, message_file, config):
        
        ts = datetime.datetime.now() - datetime.timedelta(minutes=10)
        parser = ET.XMLParser(encoding="utf-8")
        tree = ET.parse(self.db, parser=parser)
        root = tree.getroot()
        for entry in root.findall('entry'):
            if entry.attrib['type'] == "song":
                last_played = entry.find("last-played")
                if last_played is not None:
                    last_played = last_played.text
                    last_played = int(last_played)
                    last_played = datetime.datetime.fromtimestamp(last_played)
                    if last_played >= ts:
                        title = entry.find("title").text
                        message_file.write("You recently played {}\n".format(title))
