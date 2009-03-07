#
#  music.py
#  Stock plugin to calculate the system's uptime and add to the commit message.

import sqlite3
import os.path
import logging
import time
from flashbake.plugins import AbstractMessagePlugin

class Banshee(AbstractMessagePlugin):
    def init(self, config):
        """ Add an optional property for specifying a different location for the
            Banshee database. """   
        self.optionalproperty(config, 'banshee_db')
        self.optionalproperty(config, 'banshee_limit', int)
        self.optionalproperty(config, 'banshee_last_played_format')
        if self.banshee_db == None:
            logging.debug('Using default location for Banshee database.')
            self.banshee_db = os.path.join(os.path.expanduser('~'),
                   '.config', 'banshee-1', 'banshee.db')
        if self.banshee_limit == None:
            logging.debug('Using default limit of 3 most recent tracks.')
            self.banshee_limit = 3

    def addcontext(self, message_file, config):
        """ Open the Banshee database and query for the last played tracks. """
        query = """\
select t.Title, a.Name, t.LastPlayedStamp
from CoreTracks t
join CoreArtists a on t.ArtistID = a.ArtistID
order by LastPlayedStamp desc
limit %d"""
        query = query.strip() % self.banshee_limit
        conn = sqlite3.connect(self.banshee_db)
        try:
            cursor = conn.cursor()
            logging.debug('Executing %s' % query)
            cursor.execute(query)
            results = cursor.fetchall()
            message_file.write('Last %d track(s) played in Banshee:\n' % len(results))
            for result in results:
                last_played = time.localtime(result[2])
                if self.banshee_last_played_format != None:
                    logging.debug('Using format %s' % self.banshee_last_played_format)
                    last_played = time.strftime(self.banshee_last_played_format,
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
