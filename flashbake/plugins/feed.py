#
#  feed.py
#  Stock plugin that pulls latest n items from a feed by a given author.

import urllib, urllib2
import xml.dom.minidom
import logging
from urllib2 import HTTPError, URLError

connectable = True

def addcontext(message_file, control_config):
    """ Add the matching items to the commit context. """
    
    # last n items for m creator
    (title,last_items) = fetchfeed(control_config)

    if len(last_items) > 0:
        message_file.write('Last %(item_count)d entries from %(feed_title)s:\n'\
            % {'item_count' : len(last_items), 'feed_title' : title})
        for item in last_items:
          # edit the '%s' if you want to add a label, like 'Title %s' to the output
          message_file.write('%s\n' % item['title'])
          message_file.write('%s\n' % item['link'])
    else:
        message_file.write('Couldn\'t fetch entries from feed, %s.\n' % control_config.feed)

    return len(last_items) > 0

def filtertext(nodelist):
    """ Filter out all but the text node children. """
    text_value = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            text_value = text_value + node.data
    return text_value

def fetchfeed(control_config):
    """ Fetch up to the limit number of items from the specified feed with the specified
        creator. """

    # necessary machinery to fetch a web page
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())

    try:
        # open the raw RSS XML
        rss_xml = opener.open(urllib2.Request(control_config.feed)).read()

        # build a mini-dom so we can scrape out titles, descriptions
        rss_dom = xml.dom.minidom.parseString(rss_xml)

        titles = rss_dom.getElementsByTagName("title")

        feed_title = filtertext(titles[0].childNodes)

        items = rss_dom.getElementsByTagName("item")

        by_creator = []
        for child in items:
           item_creator = child.getElementsByTagName("dc:creator")[0]
           item_creator = filtertext(item_creator.childNodes).strip()
           if item_creator != control_config.author:
               continue
           title = filtertext(child.getElementsByTagName("title")[0].childNodes)
           title = title.encode('ascii', 'replace')
           link = filtertext(child.getElementsByTagName("link")[0].childNodes)
           by_creator.append({"title" : title, "link" : link})
           if control_config.limit <= len(by_creator):
               break

        return (feed_title, by_creator)
    except HTTPError, e:
        logging.error('Failed with HTTP status code %d' % e.code)
        return (None, {})
    except URLError, e:
        logging.error('Failed with reason %s.' % e.reason)
        return (None, {})
