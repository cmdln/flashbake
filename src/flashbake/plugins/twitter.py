#    Copyright 2009 Ben Snider (bensnider.com), Thomas Gideon
#    Modified 2017 Ian Paul ian@ianpaul.net
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

''' Twitter no longer publishes RSS feeds for individual users and now requires 
    all applications to authenticate with OAuth. The microblog.py script remains
    for those users who still need it to work with legacy Identica accounts.
    As of 2017, users must use this script(once it's finished) to capture their tweets. '''

from flashbake.plugins import AbstractMessagePlugin
from urllib2 import HTTPError, URLError
from xml.etree.ElementTree import ElementTree
import logging
import urllib
import twython

class Tweeter(AbstractMessagePlugin):
      def _init_(self, plugin_spec):
          AbstractMessagePlugin._init_(self, plugin_spec, True)
          self.define_property('cons_key', required = False)
          self.define_property('cons_secret', required = False)

class checkForKeys(self, message_file, config):
      '''Check for Consumer Key and Consumer Secret. If they are not present, print an error message to the terminal.'''
      if self.cons_key == None and self.cons_secret == None:
      message_file.write('This script requires you to obtain a consumer key and consumer secret from Twitter. Check the wiki for detailed instrcutions: https://github.com/commandline/flashbake/wiki/Plugins')
      return False

class TwitterWrapper(self, message_file, self.cons_key, self.cons_secret):
      APP_KEY = cons_key
      APP_SECRET = cons_secret

      twitter = Twython(APP_KEY, APP_SECRET)
      message_file.write('The app key is %s.' % APP_KEY 'The app secret is %s.' % APP_SECRET)




