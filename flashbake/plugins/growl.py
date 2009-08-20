#    copyright 2009 Jason Penney
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

# growl.py - Growl notification flashbake plugin

import flashbake
from flashbake import plugins
import fnmatch
import os
import subprocess
import glob
import logging

class Growl(plugins.AbstractNotifyPlugin):
    def __init__(self, plugin_spec):
        plugins.AbstractPlugin.__init__(self, plugin_spec)
        self.define_property('host')
        self.define_property('port')
        self.define_property('password')
        self.define_property('growlnotify')
        self.define_property('title_prefix', default='fb:')


            
    def init(self, config):
        if self.growlnotify == None:
            self.growlnotify = flashbake.find_executable('growlnotify')

        if self.growlnotify == None:
            raise plugins.PluginError(plugins.PLUGIN_ERRORS.ignorable_error,
                                      self.plugin_spec,
                                      'Could not find command, growlnotify.')

        
    # To avoid problems with a crontab entry, make sure to the network settings,
    # calling out to growlnotify only works locally/via DO if run as the user
    
    # TODO: use netgrowl.py (or wait for GNTP support to be finalized
    # so it will support Growl for Windows as well)
    def growl_notify(self,title,message):
        args = [ self.growlnotify, '--name', 'flashbake' ]
        if self.host != None:
            args += [ '--udp', '--host', self.host]
        if self.port != None:
            args += [ '--port', self.port ]
        if self.password != None:
            args += [ '--password', self.password ]

        title = ' '.join([self.title_prefix, title])
        args += ['--message', message, '--title', title]
        p = subprocess.Popen(args, stdout=subprocess.PIPE,
                             close_fds = True)

    def warn(self, hot_files, config):
        ''' Emits one message per file, with less explanation than the email plugin.
            The most common case is that one or two files will be off, a large number
            of them can be considered pathological, e.g. someone who didn't read the
            documentation about lack of support for symlinks, for instance. '''
        logging.debug(self.__whoami())
        logging.debug('Trying to warn via growl.')
        project_name = os.path.basename(hot_files.project_dir)

        [self.growl_notify('Missing in project, %s' % project_name,
                          'The file, "%s", is missing.' % file)
         for file in hot_files.not_exists]


        [self.growl_notify('Link in project, %s' % project_name,
                          'The file, "%s", is a link.' % file)
         for (file, link) in hot_files.linked_files.iteritems()
         if file == link]
        
        [self.growl_notify('Link in project, %s' % project_name,
                          'The file, "%s", is a link to %s.' % (link, file))
         for (file, link) in hot_files.linked_files.iteritems()
         if file != link]


        [self.growl_notify('External file in project, %s' % project_name,
                           'The file, "%s", exists outside of the project directory.' % file)
        for file in hot_files.outside_files]

    def notify_commit(self, to_commit, hot_files, config):
        logging.debug('Trying to notify via growl.')
        self.growl_notify(os.path.basename(hot_files.project_dir),
                          'Tracking changes to:\n' + '\n'.join(to_commit))

    def __whoami(self):
        proc = subprocess.Popen([flashbake.find_executable('whoami')], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, cwd=self.__cwd, env=self.env)
        return proc.communicate()[0]

