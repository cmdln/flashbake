#  location.py
#  Net location plugin.
#
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

from flashbake.plugins import AbstractMessagePlugin
from urllib2 import HTTPError, URLError
from xml.dom import minidom
import logging
import os.path
import re
import urllib
import urllib2



class Location(AbstractMessagePlugin):
    def __init__(self, plugin_spec):
        AbstractMessagePlugin.__init__(self, plugin_spec, True)
        self.share_property('location_location')

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
        base_url = 'http://ipinfodb.com/ip_query.php?'
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
            logging.error('Plugin, %s, failed to connect with network.' % self.__class__)
            logging.debug('Network failure reason, %s.' % e.reason)
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
            if hello_line is None:
                logging.error('Failed to parse Hello with public IP address.')
                return None
            logging.debug(hello_line)
            m = re.search('([0-9]+\.){3}([0-9]+){1}', hello_line)
            if m is None:
                logging.error('Failed to parse Hello with public IP address.')
                return None
            ip_addr = m.group(0)
            return ip_addr
        except HTTPError, e:
            logging.error('Failed with HTTP status code %d' % e.code)
            return None
        except URLError, e:
            logging.error('Plugin, %s, failed to connect with network.' % self.__class__)
            logging.debug('Network failure reason, %s.' % e.reason)
            return None
