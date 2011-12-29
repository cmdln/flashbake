#    copyright 2011 Thomas Gideon
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

# notify.py - libnotify notification flashbake plugin for standard Linux desktop notifications

from . import AbstractNotifyPlugin, AbstractPlugin, PluginError, PLUGIN_ERRORS
import flashbake
import logging
import os
import re
import subprocess
import pynotify



class Notify(AbstractNotifyPlugin):
    def __init__(self, plugin_spec):
        AbstractPlugin.__init__(self, plugin_spec)
        if not pynotify.init("icon-summary-body"):
            raise PluginError(PLUGIN_ERRORS.ignorable_error, #@UndefinedVariable
                              self.plugin_spec,
                              'Cannot initialize libnotify; are the library and the Python bindings installed?') 
        
    def __notify(self, title, message):
        n = pynotify.Notification(
            title,
            message,
            "notification-message-im")
        n.show()

    def warn(self, hot_files, config):
        ''' Emits one message per file, with less explanation than the email plugin.
            The most common case is that one or two files will be off, a large number
            of them can be considered pathological, e.g. someone who didn't read the
            documentation about lack of support for symlinks, for instance. '''
        # if calling notify locally, then the current user must be logged into the console
        if not self.__active_console():
            logging.debug('Current user does not have console access.')
            return

        logging.debug('Trying to warn via notify.')
        project_name = os.path.basename(hot_files.project_dir)

        [self.__notify('Missing in project, %s' % project_name,
                          'The file, "%s", is missing.' % file)
         for file in hot_files.not_exists]

        [self.__notify('Deleted in project, %s' % project_name,
                          'The file, "%s", has been deleted from version control.' % file)
         for file in hot_files.deleted]

        [self.__notify('Link in project, %s' % project_name,
                          'The file, "%s", is a link.' % file)
         for (file, link) in hot_files.linked_files.iteritems()
         if file == link]
        
        [self.__notify('Link in project, %s' % project_name,
                          'The file, "%s", is a link to %s.' % (link, file))
         for (file, link) in hot_files.linked_files.iteritems()
         if file != link]


        [self.__notify('External file in project, %s' % project_name,
                           'The file, "%s", exists outside of the project directory.' % file)
        for file in hot_files.outside_files]

    def notify_commit(self, to_commit, hot_files, config):
        logging.debug('Trying to notify.')
        self.__notify(os.path.basename(hot_files.project_dir),
                          'Tracking changes to:\n' + '\n'.join(to_commit))

    def __whoami(self):
        cmd = flashbake.find_executable('whoami')
        if cmd:
            proc = subprocess.Popen([cmd], stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
            return proc.communicate()[0].strip()
        else:
            return None
    
    def __active_console(self):
        user = self.__whoami()
        if not user:
            return False
        cmd = flashbake.find_executable('who')
        if not cmd:
            return False
        proc = subprocess.Popen([cmd], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        active = False
        for line in proc.communicate()[0].splitlines():
            logging.debug(line)
            m = re.match('^%s\s+pts.*$' % user, line)
            if m:
                active = True
                break
        return active

