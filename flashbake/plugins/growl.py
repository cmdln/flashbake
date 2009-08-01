# growl.py - Growl notification flashbake plugin
# by Jason Penney, jasonpenney.net

import logging, flashbake, flashbake.plugins, fnmatch, os
import subprocess, glob
from flashbake.plugins import *

class GrowlMessageFile(AbstractFilePlugin):
    """ Record Wordcount for Scrivener Files """
    def __init__(self, plugin_spec):
        AbstractFilePlugin.__init__(self, plugin_spec)

    def init(self,config):
        config.sharedproperty('growl_project_dir')
        
    def processfiles(self, hot_files, config):
        
        config.growl_project_dir = hot_files.project_dir

        if os.environ.has_key("HOME"):
            config.growl_project_dir = config.growl_project_dir.replace(os.environ["HOME"],"~")
        

class GrowlMessage(AbstractMessagePlugin):
    """ Display Growl notification for flashbake """

    def __init__(self,plugin_spec):
        AbstractMessagePlugin.__init__(self, plugin_spec, False)

    def init(self,config):
        config.sharedproperty('growl_project_dir')
        self.optionalproperty(config,'growl_host')
        self.optionalproperty(config,'growl_port')
        self.optionalproperty(config,'growl_password')
        self.optionalproperty(config,'growl_growlnotify')

        
    def addcontext(self, message_file, config):

        if self.growl_growlnotify == None:
            self.growl_growlnotify = '/usr/local/bin/growlnotify'
        if self.growl_host == None:
            self.growl_host='localhost'

        args = [ self.growl_growlnotify, '--name', 'flashbake', '--udp',
                 '--host', self.growl_host]
        if self.growl_port != None:
            args += [ '--port', self.growl_port ]
        if self.growl_password != None:
            args += [ '--password', self.growl_password ]

        message = str(config.growl_project_dir)
        args += ['--priority','High','--message', message, '--title', 'flashbake commit' ]

        p = subprocess.Popen(args, stdout=subprocess.PIPE,
                             close_fds = True)

