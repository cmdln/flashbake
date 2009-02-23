#
#  feed.py
#  Stock plugin that pulls latest n items from a feed by a given author.

import feedparser
import logging
from flashbake import PluginError, PLUGIN_ERRORS

connectable = True

def init(config):
    """ Grab any extra properties that the config parser found and are needed by this module. """
    config.requireproperty('feed_url')
    config.optionalproperty('feed_author')
    config.optionalproperty('feed_limit')
    if config.feed_limit == None:
        config.feed_limit = 5
    else:
        config.feed_limit = int(config.feed_limit)

def addcontext(message_file, config):
    """ Add the matching items to the commit context. """
    
    # last n items for m creator
    (title,last_items) = fetchfeed(config)

    if len(last_items) > 0:
        if config.feed_author == None:
            message_file.write('Last %(item_count)d entries from %(feed_title)s:\n'\
                % {'item_count' : len(last_items), 'feed_title' : title})
        else:
            message_file.write('Last %(item_count)d entries from %(feed_title)s by %(author)s:\n'\
                % {'item_count' : len(last_items), 'feed_title' : title, 'author': config.feed_author})
        for item in last_items:
          # edit the '%s' if you want to add a label, like 'Title %s' to the output
          message_file.write('%s\n' % item['title'])
          message_file.write('%s\n' % item['link'])
    else:
        message_file.write('Couldn\'t fetch entries from feed, %s.\n' % config.feed_url)

    return len(last_items) > 0

def filtertext(nodelist):
    """ Filter out all but the text node children. """
    text_value = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            text_value = text_value + node.data
    return text_value

def fetchfeed(config):
    """ Fetch up to the limit number of items from the specified feed with the specified
        creator. """

    try:
        feed = feedparser.parse(config.feed_url)

        feed_title = feed.feed.title

        logging.debug(feed.entries[0].keys())
        by_creator = []
        for entry in feed.entries:
           item_creator = entry.author
           if config.feed_author != None and item_creator != config.feed_author:
               continue
           title = entry.title
           title = title.encode('ascii', 'replace')
           link = entry.link
           by_creator.append({"title" : title, "link" : link})
           if config.feed_limit <= len(by_creator):
               break

        return (feed_title, by_creator)
    except HTTPError, e:
        logging.error('Failed with HTTP status code %d' % e.code)
        return (None, {})
    except URLError, e:
        logging.error('Failed with reason %s.' % e.reason)
        return (None, {})
