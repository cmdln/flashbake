#    Copyright 2021 Ian Paul
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

'''A plugin that scrapes your mastodon profile for n public toots. '''

from bs4 import BeautifulSoup
from urllib.request import urlopen
import itertools
import urllib.error
import logging
from flashbake.plugins import AbstractMessagePlugin

class Mastodon(AbstractMessagePlugin):
	def __init__(self, plugin_spec):
		AbstractMessagePlugin.__init__(self, plugin_spec, True)
		self.define_property('url', required=True)
		self.define_property('limit', int, False, 3)

	def addcontext(self, message_file, config):
		""" Add the specified number of toots to the commit context. """
		final_toots = self.make_dict()
		for key in final_toots:
			print (f'By {key.strip()} : {final_toots[key].strip()}')

	def fetch_soup(self):
		""" grab the Mastodon user's profile page in HTML"""
		try:
			response = urlopen(self.url)
			soup = BeautifulSoup(response.read(), 'html.parser')
			return soup
		except urllib.error.HTTPError as e:
			logging.error(f'Failed with HTTP status code {e.code}')
			return (None, {})
		except urllib.error.URLError as e:
			logging.error(f'Plugin, {self.__class__}, failed to connect with network.')
			logging.debug('Network failure reason, {e.reason}.')
			return (None, {})

	def fetch_usernames(self):
		""" grab the username/author for each toot """
		name_soup = self.fetch_soup()
		user_names = name_soup.find_all('span', class_= 'display-name__account')
		name_list = [] 
		for handle in user_names:
			raw_text = handle.text
			final = '@'.join(raw_text.split('@')[0:2])
			name_list.append(final)
		return name_list

	def fetch_toots(self):
		""" grab the actual toots """
		toot_soup = self.fetch_soup()
		toot = toot_soup.find_all('div', class_="status__content")
		toot_list=[]
		for i in toot:
			toot_list.append(i.text)
		return toot_list

	def make_dict(self):
		""" Take the usernames and toos and create a dictionary from them. Then apply the user limit. """
		name_list = self.fetch_usernames()
		toot_list = self.fetch_toots()
		res = {name_list[i]: toot_list[i] for i in range(len(name_list))}
		final_toots = dict(itertools.islice(res.items(), self.limit))
		return final_toots
