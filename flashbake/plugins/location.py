#  location.py
#  Net location plugin.

import logging
import urllib
import urllib2
import re
from urllib2 import HTTPError, URLError
from flashbake.plugins import AbstractMessagePlugin
from xml.dom import minidom
import os
import os.path

class Location(AbstractMessagePlugin):
    def __init__(self, plugin_spec):
        AbstractMessagePlugin.__init__(self, plugin_spec, True)

    def init(self, config):
        """ Shares the timezone_tz: property with timezone:TimeZone and supports
            an optional weather_city: property. """
        config.sharedproperty('location_location')

    def addcontext(self, message_file, config):
        ip_addr = self.__get_ip()
        if ip_addr == None:
            message_file.write('Failed to get public IP for geo location.\n')
            return False
        location = self.__locate_ip(ip_addr)
        if len(location) == 0:
            message_file.write('Failed to parse location data for IP address.\n')
            return False

        logging.debug(location)
        location_str = '%(City)s, %(RegionName)s' % location
        config.location_location = location_str
        message_file.write('Current location is %s based on IP %s.\n' % (location_str, ip_addr))
        return True

    def __locate_ip(self, ip_addr):
        cached = self.__load_cache()
        if cached.get('ip_addr','') == ip_addr:
            del cached['ip_addr']
            return cached
        base_url = 'http://iplocationtools.com/ip_query.php?'
        for_ip = base_url + urllib.urlencode({'ip': ip_addr})

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())

        try:
            logging.debug('Requesting page for %s.' % for_ip)

            # open the location API page
            location_xml = opener.open(urllib2.Request(for_ip)).read()

            # the weather API returns some nice, parsable XML
            location_dom = minidom.parseString(location_xml)

            # just interested in the conditions at the moment
            response = location_dom.getElementsByTagName("Response")

            if response == None or len(response) == 0:
                return dict()

            location = dict()
            for child in response[0].childNodes:
                if child.localName == None:
                    continue
                key = child.localName
                key = key.encode('ASCII', 'replace')
                location[key] = self.__get_text(child.childNodes)
            self.__save_cache(ip_addr, location)
            return location
        except HTTPError, e:
            logging.error('Failed with HTTP status code %d' % e.code)
            return {}
        except URLError, e:
            logging.error('Failed with reason %s.' % e.reason)
            return {}

    def __load_cache(self):
        home_dir = os.path.expanduser('~')
        # look for flashbake directory
        fb_dir = os.path.join(home_dir, '.flashbake')
        cache = dict()
        if not os.path.exists(fb_dir):
            return cache
        cache_name = os.path.join(fb_dir, 'ip_cache')
        if not os.path.exists(cache_name):
            return cache
        cache_file = open(cache_name, 'r')
        try:
            for line in cache_file:
                tokens = line.split(':')
                key = tokens[0]
                value = tokens[1].strip()
                if key.startswith('location.'):
                    key = key.replace('location.', '')
                cache[key] = value
            logging.debug('Loaded cache %s' % cache)
        finally:
            cache_file.close()
        return cache

    def __save_cache(self, ip_addr, location):
        home_dir = os.path.expanduser('~')
        # look for flashbake directory
        fb_dir = os.path.join(home_dir, '.flashbake')
        if not os.path.exists(fb_dir):
            os.mkdir(fb_dir)
        cache_file = open(os.path.join(fb_dir, 'ip_cache'), 'w')
        try:
            cache_file.write('ip_addr:%s\n' % ip_addr)
            for key in location.iterkeys():
                cache_file.write('location.%s:%s\n' % (key, location[key]))
        finally:
            cache_file.close()

    def __get_text(self, node_list):
        text_value = ''
        for node in node_list:
            if node.nodeType != node.TEXT_NODE:
                continue;
            text_value += node.data
        return text_value

    def __get_ip(self):
        no_reply = 'http://www.noreply.org'
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())

        try:
            # open the weather API page
            ping_reply = opener.open(urllib2.Request(no_reply)).read()
            hello_line = None
            for line in ping_reply.split('\n'):
                if line.find('Hello') > 0:
                    hello_line = line.strip()
                    break
            if hello_line == None:
                message_file.write('Failed to parse Hello with public IP address.')
            logging.debug(hello_line)
            m = re.search('([0-9]+\.){3}([0-9]+){1}', hello_line)
            if m == None:
                message_file.write('Failed to parse Hello with public IP address.')
            ip_addr = m.group(0)
            return ip_addr
        except HTTPError, e:
            logging.error('Failed with HTTP status code %d' % e.code)
            return None
        except URLError, e:
            logging.error('Failed with reason %s.' % e.reason)
            return None
