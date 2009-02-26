#
#  feed.py
#  Stock plugin that pulls latest n items from a feed by a given author.

import feedparser
import logging
from flashbake.plugins import AbstractMessagePlugin

class Feed(AbstractMessagePlugin):
    def __init__(self, plugin_spec):
        AbstractMessagePlugin.__init__(self, plugin_spec, True)

    def init(self, config):
        """ Grab any extra properties that the config parser found and are needed by this module. """
        self.requireproperty(config, 'feed_url')
        self.optionalproperty(config, 'feed_author')
        self.optionalproperty(config, 'feed_limit', int)
        if self.feed_limit == None:
            self.feed_limit = 5

    def addcontext(self, message_file, config):
        """ Add the matching items to the commit context. """
        
        # last n items for m creator
        (title,last_items) = self.__fetchfeed()

        if len(last_items) > 0:
            if self.feed_author == None:
                message_file.write('Last %(item_count)d entries from %(feed_title)s:\n'\
                    % {'item_count' : len(last_items), 'feed_title' : title})
            else:
                message_file.write('Last %(item_count)d entries from %(feed_title)s by %(author)s:\n'\
                    % {'item_count' : len(last_items), 'feed_title' : title, 'author': self.feed_author})
            for item in last_items:
              # edit the '%s' if you want to add a label, like 'Title %s' to the output
              message_file.write('%s\n' % item['title'])
              message_file.write('%s\n' % item['link'])
        else:
            message_file.write('Couldn\'t fetch entries from feed, %s.\n' % self.feed_url)

        return len(last_items) > 0

    def __fetchfeed(self):
        """ Fetch up to the limit number of items from the specified feed with the specified
            creator. """

        try:
            feed = feedparser.parse(self.feed_url)

            feed_title = feed.feed.title

            by_creator = []
            for entry in feed.entries:
               item_creator = entry.author
               if self.feed_author != None and item_creator != self.feed_author:
                   continue
               title = entry.title
               title = title.encode('ascii', 'replace')
               link = entry.link
               by_creator.append({"title" : title, "link" : link})
               if self.feed_limit <= len(by_creator):
                   break

            return (feed_title, by_creator)
        except HTTPError, e:
            logging.error('Failed with HTTP status code %d' % e.code)
            return (None, {})
        except URLError, e:
            logging.error('Failed with reason %s.' % e.reason)
            return (None, {})
