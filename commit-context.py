#
#  commit-context.py
#  Build up some descriptive context for automatic commit to git
#
#  Created by Thomas Gideon on 1/25/2009
#  TODO add license block

if __name__ == "__main__":
    import sys
    import urllib, urllib2
    import xml.dom.minidom
    import os

    zone = os.environ.get("TZ")
    if None == zone:
        zone_file = open('/etc/timezone')
        zone = zone_file.read()
    zone = zone.replace("_", " ")
    print 'Current time zone is ', zone

    tokens = zone.split("/")
    city = tokens[1]

    print 'Weather for', city

    baseurl = 'http://www.google.com/ig/api?'
    for_city = baseurl + urllib.urlencode({'weather': city})

    print for_city

    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())

    weather = opener.open(urllib2.Request(for_city)).read()

    print weather

    doc = xml.dom.minidom.parseString(weather)

    current = doc.getElementsByTagName("current_conditions")
    for child in current.childNodes:
       print child.localName, child.nodeValue
    
    print "system up time"
    print "last 3 entries from a feed"
