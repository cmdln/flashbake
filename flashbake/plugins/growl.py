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

class Growl(plugins.AbstractNotifyPlugin):
    def __init__(self, plugin_spec):
        plugins.AbstractPlugin.__init__(self, plugin_spec)
        self.define_property('host', default='localhost')
        self.define_property('port')
        self.define_property('password',required=True)
        self.define_property('growlnotify')
        self.define_property('title_prefix', default='fb:')


            
    def init(self, config):
        if self.growlnotify == None:
            self.growlnotify = flashbake.find_executable('growlnotify')

        if self.growlnotify == None:
            raise plugins.PluginError(plugins.PLUGIN_ERRORS.ignorable_error,
                                      self.plugin_spec,
                                      'Could not find command, growlnotify.')

        

    # uses network notification because they don't cause issues when run
    # from cron jobs
    
    # TODO: use netgrowl.py (or wait for GNTP support to be finalized
    # so it will support Growl for Windows as well)
    def growl_notify(self,title,message):        
        args = [ self.growlnotify, '--name', 'flashbake', '--udp',
                 '--host', self.host]
        if self.port != None:
            args += [ '--port', self.port ]
        if self.password != None:
            args += [ '--password', self.password ]

        title = ' '.join([self.title_prefix, title])
        args += ['--message', message, '--title', title]
        p = subprocess.Popen(args, stdout=subprocess.PIPE,
                             close_fds = True)

    # TODO: flesh this message out (how to keep useful without being too HUGE)
    def warn(self, hot_files, config):
        args = config
        self.growl_notify(os.path.basename(hot_files.project_dir), 'issue during commit')


    def notify_commit(self, to_commit, hot_files, config):
        self.growl_notify(os.path.basename(hot_files.project_dir),
                          'Tracking changes to:\n' + '\n'.join(to_commit))

