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
    As of 2017, users must use this script to capture their tweets. '''

from flashbake.plugins import AbstractMessagePlugin

class Tweeter(AbstractMessagePlugin):
      def __init__(self, plugin_spec):
          AbstractMessagePlugin.__init__(self, plugin_spec, True)
          self.define_property('cons_key', required=False)
          self.define_property('cons_sec', required=False)

      def addcontext(self, message_file, config):
          if self.cons_key == None and self.cons_sec == None:
              message_file.write('Sorry, you need a consumer key and secret to commit your tweets')
          return True 



