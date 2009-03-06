#  microblog.py
#  by Ben Snider, bensnider.com

import logging, urllib
from urllib2 import HTTPError, URLError
from xml.etree.ElementTree import ElementTree
from flashbake.plugins import AbstractMessagePlugin

class Twitter(AbstractMessagePlugin):
    
    def __init__(self, plugin_spec):
        AbstractMessagePlugin.__init__(self, plugin_spec, True)
        self.service_name = plugin_spec.split(':')[-1]
        self.property_prefix = '_'.join(self.service_name.lower().strip().split(' '))
        self.service_url = 'http://twitter.com'
        self.optional_field_info = { \
            'source':{'path':'source', 'transform':propercase}, \
            'location':{'path':'user/location', 'transform':propercase}, \
            'favorited':{'path':'favorited', 'transform':propercase}, \
            'tweeted_on': {'path':'created_at', 'transform':utc_to_local}, \
        }
        self.requiredproperties = [self.property_prefix+'_user']
        self.optionalproperties = [self.property_prefix+'_limit', self.property_prefix+'_optional_fields']
    
    def init(self, config):
        for prop in self.requiredproperties:
            self.requireproperty(config, prop)
        for prop in self.optionalproperties:
            self.optionalproperty(config, prop)
        
        self.__formatproperties(config)
        self.__setoptionalfields(config)
        
        # simple user xml feed
        self.twitter_url = '%(url)s/statuses/user_timeline/%(user)s.xml?count=%(limit)d' % \
            {'url':self.service_url, \
            'user':self.__dict__[self.property_prefix+'_user'], \
            'limit':self.__dict__[self.property_prefix+'_limit']} \
    
    def __formatproperties(self, config):
        limit_property_name = self.property_prefix+'_limit'
        
        # short circuit this conditional so we don't get a TypeError 
        if (self.__dict__[limit_property_name] == None or int(self.__dict__[limit_property_name]) < 1):
            self.__dict__[limit_property_name] = 5
        else:
            self.__dict__[limit_property_name] = int(self.__dict__[limit_property_name])
            # respect the twitter api limits
            if (self.__dict__[limit_property_name] > 200):
                logging.warn('Please use a limit <= 200.');
                self.__dict__[limit_property_name] = 200
    
    def __setoptionalfields(self, config):
        optional_fields_name = self.property_prefix+'_optional_fields'
        
        # We don't have to worry about a KeyError here since this property
        # should have been set to None by self.setoptionalproperty.
        if (self.__dict__[optional_fields_name] == None):
            self.__dict__[optional_fields_name] = []
        else:
            # get the optional fields, split on commas
            fields = self.__dict__[optional_fields_name].strip().split(',')
            newFields = []
            for field in fields:
                field = field.strip()
                # check if they are allowed and not a dupe
                if (field in self.optional_field_info and field not in newFields):
                    # if so we push them onto the optional fields array, otherwise ignore
                    newFields.append(field)
            # finally sort the list so its the same each run, provided the config is the same
            newFields.sort()
            self.__dict__[optional_fields_name] = newFields
        
    def addcontext(self, message_file, config):
        (title, last_tweets) = self.__fetchitems(config)
        
        if (len(last_tweets) > 0 and title != None):
            to_file = ('Last %(item_count)d %(service_name)s messages from %(twitter_title)s:\n' \
                % {'item_count' : len(last_tweets), 'twitter_title' : title, 'service_name':self.service_name})
            
            i=1
            for item in last_tweets:
                to_file += ('%d) %s\n' % (i, item['tweet']))
                for field in self.__dict__[self.property_prefix+'_optional_fields']:
                    to_file += ('\t%s: %s\n' % (propercase(field), item[field]))
                i+=1
            
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
            logging.error('Failed with reason %s.' % e.reason)
            return results
        except IOError:
            logging.error('Socket error.')
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
            for field in self.__dict__[self.property_prefix+'_optional_fields']:
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
    import calendar, time, datetime
    # Discard the timezone, python dont like it, and it seems to always be
    # set to UTC, even if the user has their timezone set.
    t = t.replace('+0000 ', '')
    # might asplode
    return datetime.datetime.fromtimestamp((calendar.timegm(datetime.datetime.strptime(t, '%a %b %d %H:%M:%S %Y').timetuple()))).strftime("%A, %b. %d, %Y at %I:%M%p %z")
