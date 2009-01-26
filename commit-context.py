#
#  commit-context.py
#  Build up some descriptive context for automatic commit to git
#
#  Created by Thomas Gideon on 1/25/2009
#  TODO add license block

import sys
import urllib, urllib2
import xml.dom.minidom
import os
import string

def get_uptime():
    """ copied with blanket permission from
        http://thesmithfam.org/blog/2005/11/19/python-uptime-script/ """

    try:
         f = open( "/proc/uptime" )
         contents = f.read().split()
         f.close()
    except:
        return "Cannot open uptime file: /proc/uptime"

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

def go():
    # check the environment for the zone value
    zone = os.environ.get("TZ")

    # some desktops don't set the env var but /etc/timezone should
    # have the value regardless
    if None == zone:
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

    print 'Current time zone is %s' % zone
    # there is also an entry for the key, wind_condition, in the weather
    # dictionary
    print 'Current weather is %(condition)s (%(temp_f)sF/%(temp_c)sC) %(humidity)s' % weather
    print 'System has been up %s ' % uptime
    print 'Last 3 entries from a feed'

# call go() when this module is executed as the main script
if __name__ == "__main__": go()
