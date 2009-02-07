#!/usr/bin/env python
#
#  commit-context.py
#  Build up some descriptive context for automatic commit to git
#
#  version 0.3 - added checks for errors on network calls
#
#  history
#  version 0.2 - added she-bang
#  version 0.1 - functionally complete
#
#  Created by Thomas Gideon (cmdln@thecommandline.net) on 1/25/2009
#  Provided as-is, with no warranties
#  License: http://creativecommons.org/licenses/by-nc-sa/3.0/us/ 

import sys
import urllib, urllib2
import xml.dom.minidom
import os
import os.path
import string
import random

def get_uptime():
    """ copied with blanket permission from
        http://thesmithfam.org/blog/2005/11/19/python-uptime-script/ """

    try:
         f = open( "/proc/uptime" )
         contents = f.read().split()
         f.close()
    except:
        return None

    total_seconds = float(contents[0])

    # Helper vars:
    MINUTE  = 60
    HOUR    = MINUTE * 60
    DAY     = HOUR * 24

    # Get the days, hours, etc:
    days    = int( total_seconds / DAY )
    hours   = int( ( total_seconds % DAY ) / HOUR )
    minutes = int( ( total_seconds % HOUR ) / MINUTE )
    seconds = int( total_seconds % MINUTE )

    # Build up the pretty string (like this: "N days, N hours, N minutes, N seconds")
    string = ""
    if days> 0:
        string += str(days) + " " + (days == 1 and "day" or "days" ) + ", "
    if len(string)> 0 or hours> 0:
        string += str(hours) + " " + (hours == 1 and "hour" or "hours" ) + ", "
    if len(string)> 0 or minutes> 0:
        string += str(minutes) + " " + (minutes == 1 and "minute" or "minutes" ) + ", "
    string += str(seconds) + " " + (seconds == 1 and "second" or "seconds" )

    return string

def get_weather(city):
    """ This relies on Google's unpublished weather API which may change without notice. """

    # unpublished API that iGoogle uses for its weather widget
    baseurl = 'http://www.google.com/ig/api?'
    # encode the sole paramtere
    for_city = baseurl + urllib.urlencode({'weather': city})

    # necessary machinery to fetch a web page
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())

    try:
        # open the weather API page
        weather_xml = opener.open(urllib2.Request(for_city)).read()

        # the weather API returns some nice, parsable XML
        weather_dom = xml.dom.minidom.parseString(weather_xml)

        # just interested in the conditions at the moment
        current = weather_dom.getElementsByTagName("current_conditions")

        weather = {}
        for child in current[0].childNodes:
           if child.localName == 'icon':
               continue
           weather[child.localName] = child.getAttribute('data').strip()

        return weather
    except:
        return {}

def get_text(nodelist):
    text_value = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            text_value = text_value + node.data
    return text_value

def get_rss(url, limit, creator):
    """ Fetch up to the limit number of items from the specified feed with the specified
        creator. """

    # necessary machinery to fetch a web page
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())

    try:
        # open the raw RSS XML
        rss_xml = opener.open(urllib2.Request(url)).read()

        # build a mini-dom so we can scrape out titles, descriptions
        rss_dom = xml.dom.minidom.parseString(rss_xml)

        titles = rss_dom.getElementsByTagName("title")

        feed_title = get_text(titles[0].childNodes)

        items = rss_dom.getElementsByTagName("item")

        by_creator = []
        for child in items:
           item_creator = child.getElementsByTagName("dc:creator")[0]
           item_creator = get_text(item_creator.childNodes).strip()
           if item_creator != creator:
               continue
           title = get_text(child.getElementsByTagName("title")[0].childNodes)
           link = get_text(child.getElementsByTagName("link")[0].childNodes)
           by_creator.append({"title" : title, "link" : link})
           if limit <= len(by_creator):
               break

        return (feed_title, by_creator)
    except:
        return (None, {})

def build_message_file(feed_url, item_limit, by_line):
    # check the environment for the zone value
    zone = os.environ.get("TZ")

    # some desktops don't set the env var but /etc/timezone should
    # have the value regardless
    if None == zone:
        if not os.path.exists('/etc/timezone'):
            print 'Could not get TZ from env var or /etc/timezone.'
            sys.exit(1)
        zone_file = open('/etc/timezone')
        zone = zone_file.read()
        zone = zone.replace("\n", "")

    tokens = zone.split("/")
    if len(tokens) != 2:
        print 'Zone id, "', zone, '", doesn''t appear to contain a city.'
        # return non-zero so calling shell script can catch
        return 1

    city = tokens[1]
    # ISO id's have underscores, convert to spaces for the Google API
    city = city.replace("_", " ")

    # call the Google weather API with the city
    weather = get_weather(city)

    # with thanks to Dave Smith
    uptime = get_uptime()
    
    # last n items for m creator
    (title,last_items) = get_rss(feed_url, item_limit, by_line)

    msg_filename = '/tmp/git_msg_%d' % random.randint(0,1000)

    # try to avoid clobbering another process running this script
    while os.path.exists(msg_filename):
        msg_filename = '/tmp/git_msg_%d' % random.randint(0,1000)

    message_file = open(msg_filename, 'w')
    try:
        message_file.write('Current time zone is %s\n' % zone)
        if len(weather) > 0:
            # there is also an entry for the key, wind_condition, in the weather
            # dictionary
            message_file.write('Current weather is %(condition)s (%(temp_f)sF/%(temp_c)sC) %(humidity)s\n'\
                    % weather)
        else:
            message_file.write('Couldn\'t fetch current weather.\n')
        if uptime == None:
            message_file.write('Couldn\'t determine up time.\n')
        else:
            message_file.write('System has been up %s\n' % uptime)
        if len(last_items) > 0:
            message_file.write('Last %(item_count)d entries from %(feed_title)s:\n'\
                % {'item_count' : len(last_items), 'feed_title' : title})
            for item in last_items:
              # edit the '%s' if you want to add a label, like 'Title %s' to the output
              message_file.write('%s\n' % item['title'])
              message_file.write('%s\n' % item['link'])
        else:
            message_file.write('Couldn\'t fetch entries from feed, %s.\n' % feed_url)
        if len(weather) == 0 and len(last_items) == 0:
            message_file.write('System is most likely offline.')
    finally:
        message_file.close()
    return msg_filename

# call go() when this module is executed as the main script
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print '%s <feed url> <item limit> <author name>' % sys.argv[0]
        sys.exit(1)
    msg_filename = build_message_file(sys.argv[1], int(sys.argv[2]), sys.argv[3])
    message_file = open(msg_filename, 'r')

    try:
        for line in message_file:
            print line.strip()
    finally:
        message_file.close()
