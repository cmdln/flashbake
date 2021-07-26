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
import urllib.request
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
                message_file.write('Last {} entries from {}:\n'\
                    .format(*[len(last_items), title]))
            else:
                message_file.write('Last {} entries from {} by {}:\n'\
                    .format(*[len(last_items), title, self.author]))
            for item in last_items:
                
                message_file.write(f'{item["title"]}\n')
                message_file.write(f'{item["link"]}\n')
        else:
            message_file.write('Couldn\'t fetch entries from feed, {}\n'.format(self.url))

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
                try:
                    if self.author != None and entry.author != self.author:
                        continue
                    title = entry.title
                    title = title.encode('utf-8', 'replace').decode('utf-8')
                    link = entry.link
                    by_creator.append({"title" : title, "link" : link})
                    if self.limit <= len(by_creator):
                        break
                except:
                    logging.error('There are no entries for the specified author.')
                    return (None, {})

            return (feed_title, by_creator)
        except urllib.error.HTTPError as e:
            logging.error(f'Failed with HTTP status code {e.code}')
            return (None, {})
        except urllib.error.URLError as e:
            logging.error(f'Plugin, {self.__class__}, failed to connect with network.')
            logging.debug('Network failure reason, {e.reason}.')
            return (None, {})
