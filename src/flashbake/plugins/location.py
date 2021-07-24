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
import urllib.request
from urllib.parse import urlencode
from xml.dom import minidom
import logging
import os.path
import re
import json
from requests import get



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
        location_str = '%(city)s, %(regionName)s' % location
        config.location_location = location_str
        message_file.write(f'Current location is {location_str} based on IP {ip_addr}.\n')
        return True

    def __locate_ip(self, ip_addr):
        cached = self.__load_cache()
        if cached.get('ip_addr','') == ip_addr:
            del cached['ip_addr']
            return cached
        base_url = 'http://ip-api.com/json/'
        for_ip = base_url + (ip_addr)

        try:
            logging.debug(f'Requesting page for {for_ip}.' )

            # open the location API page
            location_xml = urllib.request.Request(for_ip)
            with urllib.request.urlopen(location_xml) as response:
                the_page = response.read()

            data = json.loads(the_page)

            location = dict()

            for k,v in data.items():
              location[k] = v

            return location
        except urllib.error.HTTPError as e:
            logging.error(f'Failed with HTTP status code {e.code}')
            return {}
        except urllib.error.URLError as e:
            logging.error(f'Plugin, {self.__class__}, failed to connect with network.')
            logging.debug(f'Network failure reason, {e.reason}.')
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
            logging.debug(f'Loaded cache {cache}')
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
            cache_file.write(f'ip_addr:{ip_adder}\n')
            for key in location.keys():
                cache_file.write(f'location.{key}:{location[key]}\n' )
        finally:
            cache_file.close()

    def __get_text(self, node_list):
        text_value = ''
        for node in node_list:
            if node.nodeType != node.TEXT_NODE:
                continue
            text_value += node.data
        return text_value

    def __get_ip(self):
        ip_me = get('https://api.ipify.org').text

        try:
            ip_addr = ip_me
            return ip_addr
        except urllib.error.HTTPError as e:
            logging.error(f'Failed with HTTP status code {e.code}' )
            return None
        except urllib.error.URLError as e:
            logging.error(f'Plugin, {self.__class__}, failed to connect with network.' )
            logging.debug(f'Network failure reason, {e.reason}.')
            return None
