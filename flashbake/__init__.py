import os
import logging
import sys
import commands
from types import *

# from http://pypi.python.org/pypi/enum/
from enum import Enum
PLUGIN_ERRORS = Enum('unknown_plugin',
        'missing_attribute',
        'invalid_attribute',
        'missing_property'
        )

class PluginError(Exception):
    def __init__(self, reason, name):
        self.reason = reason
        self.name = name
    def __str__(self):
        return '%s: %s' % (self.reason, self.name)

class ControlConfig:
    """
    Gather control options parsed out of the dot-control file in a project.
    """

    def __init__(self):
        self.extra_props = dict()

        self.email = None
        self.notice_to = None
        self.notice_from = None
        self.smtp_port = 25

        self.int_props = list()
        self.int_props.append('smtp_port')

        self.plugin_names = list()
        self.plugins = list()

    def init(self):
        """
        Do any property clean up, after parsing but before use
        """

        if self.notice_from == None and self.notice_to != None:
            self.notice_from = self.notice_to

        if len(self.plugin_names) == 0:
            logging.debug('No plugins configured, enabling the stock set.')
            self.addplugins(['flashbake.plugins.timezone',
                    'flashbake.plugins.weather',
                    'flashbake.plugins.uptime',
                    'flashbake.plugins.feed'])

        self.initplugins()

    def requireproperty(self, name):
        """ Useful to plugins to express a property that is required in the
            dot-control file and to move it from the extra_props dict to a
            property of the config. """
        if not name in self.extra_props:
            raise PluginError(PLUGIN_ERRORS.missing_property, name)

        self.optionalproperty(name)

    def optionalproperty(self, name):
        value = None

        if name in self.extra_props:
            value = self.extra_props[name]
            del self.extra_props[name]

        self.__dict__[name] = value

    def addplugins(self, plugin_names):
        self.plugin_names = self.plugin_names + plugin_names

    def initplugins(self):
        for plugin_name in self.plugin_names:
            plugin = self.initplugin(plugin_name)
            self.plugins.append(plugin)

    def initplugin(self, plugin_name):
        """ Initialize a plugin, including vetting that it meets the correct
            protocol; not private so it can be used in testing. """
        try:
            __import__(plugin_name)
        except ImportError:
            logging.warn('Invalid module, %s' % plugin_name)
            raise PluginError(PLUGIN_ERRORS.unknown_plugin, plugin_name)

        plugin_module = sys.modules[plugin_name]

        self.__checkattr(plugin_module, 'connectable', bool)
        self.__checkattr(plugin_module, 'addcontext', FunctionType)

        if 'init' in plugin_module.__dict__ and isinstance(plugin_module.__dict__['init'], FunctionType):
            plugin_module.init(self)

        return plugin_module

    def __checkattr(self, plugin, name, expected_type):
        if name not in plugin.__dict__:
            logging.warn('Plugin, %s, must have a %s attribute.' % (plugin.__name__, name))
            raise PluginError(PLUGIN_ERRORS.missing_attribute, name)

        if not isinstance(plugin.__dict__[name], expected_type):
            logging.warn('%s attribute of plugin, %s, must be %s.' % (name, plugin.__name__, str(expected_type)))
            raise PluginError(PLUGIN_ERRORS.invalid_attribute, name)

class ParseResults:
    """
    Track the files as they are parsed and manipulated with regards to their git
    status and the dot-control file.
    """
    def __init__(self):
        self.linked_files = dict()
        self.control_files = set()
        self.not_exists = set()
        self.to_add = set()

    def addfile(self, filename):
        link = self.checklink(filename)

        if link == None:
            self.control_files.add(filename)
        else:
            self.linked_files[filename] = link

    def checklink(self, filename):
        if os.path.islink(filename):
           return filename
        directory = os.path.dirname(filename)

        while (len(directory) > 0):
            if os.path.islink(directory):
                return directory
            directory = os.path.dirname(directory)
        return None

    def contains(self, filename):
        return filename in self.control_files

    def remove(self, filename):
        self.control_files.remove(filename)

    def putabsent(self, filename):
        self.not_exists.add(filename)

    def putneedsadd(self, filename):
        self.to_add.add(filename)

    def warnlinks(self):
        # print warnings for linked files
        for (filename, link) in self.linked_files.iteritems():
            logging.info('%s is a link or its directory path contains a link.' % filename)

    def addorphans(self, control_config):
        if len(self.to_add) == 0:
            return

        message_file = context.buildmessagefile(control_config)

        add_template = 'git add "%s"'
        git_commit = 'git commit -F %(msg_filename)s %(filenames)s'
        file_template = ' "%s"'
        to_commit = ''
        for orphan in self.to_add:
            logging.debug('Adding %s.' % orphan)
            add_output = commands.getoutput(add_template % orphan)
            to_commit += file_template % orphan

        logging.info('Adding new files, %s.' % to_commit)
        # consolidate the commit to be friendly to how git normally works
        git_commit = git_commit % {'msg_filename' : message_file, 'filenames' : to_commit}
        logging.debug(git_commit)
        if not control_config.dryrun:
            commit_output = commands.getoutput(git_commit)
            logging.debug(commit_output)

        os.remove(message_file)

    def needsnotice(self):
        return len(self.not_exists) > 0 or len(self.linked_files) > 0
