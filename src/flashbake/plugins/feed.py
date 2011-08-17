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

'''  feed.py - Stock plugin that pulls latest n items from a feed by a given author. '''

import feedparser
import logging
from urllib2 import HTTPError, URLError
from flashbake.plugins import AbstractMessagePlugin



class Feed(AbstractMessagePlugin):
    def __init__(self, plugin_spec):
        AbstractMessagePlugin.__init__(self, plugin_spec, True)
        self.define_property('url', required=True)
        self.define_property('author')
        self.define_property('limit', int, False, 5)

    def addcontext(self, message_file, config):
        """ Add the matching items to the commit context. """

        # last n items for m creator
        (title, last_items) = self.__fetchfeed()

        if len(last_items) > 0:
            if self.author == None:
                message_file.write('Last %(item_count)d entries from %(feed_title)s:\n'\
                    % {'item_count' : len(last_items), 'feed_title' : title})
            else:
                message_file.write('Last %(item_count)d entries from %(feed_title)s by %(author)s:\n'\
                    % {'item_count' : len(last_items), 'feed_title' : title, 'author': self.author})
            for item in last_items:
                # edit the '%s' if you want to add a label, like 'Title %s' to the output
                message_file.write('%s\n' % item['title'])
                message_file.write('%s\n' % item['link'])
        else:
            message_file.write('Couldn\'t fetch entries from feed, %s.\n' % self.url)

        return len(last_items) > 0

    def __fetchfeed(self):
        """ Fetch up to the limit number of items from the specified feed with the specified
            creator. """

        try:
            feed = feedparser.parse(self.url)

            if not 'title' in feed.feed:
                logging.info('Feed title is empty, feed is either malformed or unavailable.')
                return (None, {})

            feed_title = feed.feed.title

            by_creator = []
            for entry in feed.entries:
                if self.author != None and entry.author != self.author:
                    continue
                title = entry.title
                title = title.encode('ascii', 'replace')
                link = entry.link
                by_creator.append({"title" : title, "link" : link})
                if self.limit <= len(by_creator):
                    break

            return (feed_title, by_creator)
        except HTTPError, e:
            logging.error('Failed with HTTP status code %d' % e.code)
            return (None, {})
        except URLError, e:
            logging.error('Plugin, %s, failed to connect with network.' % self.__class__)
            logging.debug('Network failure reason, %s.' % e.reason)
            return (None, {})
