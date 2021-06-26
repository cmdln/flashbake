#    Copyright 2017 Ian Paul
#    Copyright 2009 Thomas Gideon
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

''' Twitter plugin pulls the last 'n' tweets from your Twitter profile including retweets. '''

import tweepy

from flashbake.plugins import AbstractMessagePlugin

class Twitter(AbstractMessagePlugin):
      def __init__(self, plugin_spec):
          AbstractMessagePlugin.__init__(self, plugin_spec, True)
          self.define_property('consumer_key', required=False)
          self.define_property('consumer_secret', required=False)
          self.define_property('access_key', required=False)
          self.define_property('access_secret', required=False)
          self.define_property('tweet_limit', required=True)
          self.define_property('username', required=True)

      def addcontext(self, message_file, config):
          auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
          auth.set_access_token(self.access_key, self.access_secret)
          api = tweepy.API(auth)

          public_tweets = api.user_timeline(screen_name = self.username, count = self.tweet_limit, tweet_mode='extended')
          for tweet in public_tweets:
              if hasattr(tweet, 'retweeted_status'):
                  message_file.write(str('RT @' + tweet.retweeted_status.user.screen_name + ': ' + tweet.retweeted_status.full_text) + '\n')
              else:
                  message_file.write(str('By Me: ' + tweet.full_text) + '\n')
