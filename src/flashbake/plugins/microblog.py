#    copyright 2009 Ben Snider (bensnider.com), Thomas Gideon
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
'''  microblog.py - microblog plugins by Ben Snider, bensnider.com '''

from flashbake.plugins import AbstractMessagePlugin
from urllib2 import HTTPError, URLError
from xml.etree.ElementTree import ElementTree
import logging
import urllib



class Twitter(AbstractMessagePlugin):
    def __init__(self, plugin_spec):
        AbstractMessagePlugin.__init__(self, plugin_spec, True)
        self.service_url = 'http://twitter.com'
        self.optional_field_info = { \
            'source':{'path':'source', 'transform':propercase}, \
            'location':{'path':'user/location', 'transform':propercase}, \
            'favorited':{'path':'favorited', 'transform':propercase}, \
            'tweeted_on': {'path':'created_at', 'transform':utc_to_local}, \
        }
        self.define_property('user', required=True)
        self.define_property('limit', int, False, 5)
        self.define_property('optional_fields')

    def init(self, config):
        if self.limit > 200:
            logging.warn('Please use a limit <= 200.');
            self.limit = 200

        self.__setoptionalfields(config)

        # simple user xml feed
        self.twitter_url = '%(url)s/statuses/user_timeline/%(user)s.xml?count=%(limit)d' % {
            'url':self.service_url,
            'user':self.user,
            'limit':self.limit}

    def __setoptionalfields(self, config):
        # We don't have to worry about a KeyError here since this property
        # should have been set to None by self.setoptionalproperty.
        if (self.optional_fields == None):
            self.optional_fields = []
        else:
            # get the optional fields, split on commas
            fields = self.optional_fields.strip().split(',')
            newFields = []
            for field in fields:
                field = field.strip()
                # check if they are allowed and not a dupe
                if (field in self.optional_field_info and field not in newFields):
                    # if so we push them onto the optional fields array, otherwise ignore
                    newFields.append(field)
            # finally sort the list so its the same each run, provided the config is the same
            newFields.sort()
            self.optional_fields = newFields

    def addcontext(self, message_file, config):
        (title, last_tweets) = self.__fetchitems(config)

        if (len(last_tweets) > 0 and title != None):
            to_file = ('Last %(item_count)d %(service_name)s messages from %(twitter_title)s:\n' \
                % {'item_count' : len(last_tweets), 'twitter_title' : title, 'service_name':self.service_name})

            i = 1
            for item in last_tweets:
                to_file += ('%d) %s\n' % (i, item['tweet']))
                for field in self.optional_fields:
                    to_file += ('\t%s: %s\n' % (propercase(field), item[field]))
                i += 1

            logging.debug(to_file.encode('UTF-8'))
            message_file.write(to_file.encode('UTF-8'))
        else:
            message_file.write('Couldn\'t fetch entries from feed, %s.\n' % self.twitter_url)

        return len(last_tweets) > 0

    def __fetchitems(self, config):
        ''' We fetch the tweets from the configured url in self.twitter_url,
        and return a list containing the formatted title and an array of
        tweet dictionaries that contain at least the 'tweet' key along with
        any optional fields. The 
        '''
        results = [None, []]

        try:
            twitter_xml = urllib.urlopen(self.twitter_url)
        except HTTPError, e:
            logging.error('Failed with HTTP status code %d' % e.code)
            return results
        except URLError, e:
            logging.error('Plugin, %s, failed to connect with network.' % self.__class__)
            logging.debug('Network failure reason, %s.' % e.reason)
            return results
        except IOError:
            logging.error('Plugin, %s, failed to connect with network.' % self.__class__)
            logging.debug('Socket error.')
            return results

        tree = ElementTree()
        tree.parse(twitter_xml)

        status = tree.find('status')
        if (status == None):
            return results
        # after this point we are pretty much guaranteed that we won't get an
        # exception or None value, provided the twitter xml stays the same
        results[0] = propercase(status.find('user/name').text)

        for status in tree.findall('status'):
            tweet = {}
            tweet['tweet'] = status.find('text').text
            for field in self.optional_fields:
                tweet[field] = status.find(self.optional_field_info[field]['path']).text
                if ('transform' in self.optional_field_info[field]):
                    tweet[field] = self.optional_field_info[field]['transform'](tweet[field])
            results[1].append(tweet)

        return results


class Identica(Twitter):

    def __init__(self, plugin_spec):
        Twitter.__init__(self, plugin_spec)
        self.service_url = 'http://identi.ca/api'
        self.optional_field_info['created_on'] = self.optional_field_info['tweeted_on']
        del self.optional_field_info['tweeted_on']


def propercase(string):
    ''' Returns the string with _ replaced with spaces and the whole string
    should be title cased. '''
    string = string.replace('_', ' ')
    string = string.title()
    return string


def utc_to_local(t):
    ''' ganked from http://feihonghsu.blogspot.com/2008/02/converting-from-local-time-to-utc.html '''
    import calendar, datetime
    # Discard the timezone, python dont like it, and it seems to always be
    # set to UTC, even if the user has their timezone set.
    t = t.replace('+0000 ', '')
    # might asplode
    return datetime.datetime.fromtimestamp((calendar.timegm(datetime.datetime.strptime(t, '%a %b %d %H:%M:%S %Y').timetuple()))).strftime("%A, %b. %d, %Y at %I:%M%p %z")
