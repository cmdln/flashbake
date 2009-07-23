#    copyright 2009 Thomas Gideon
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

from enum import Enum
import logging

PLUGIN_ERRORS = Enum(
        'invalid_plugin',
        'invalid_type',
        'unknown_plugin',
        'missing_attribute',
        'invalid_attribute',
        'missing_property',
        'ignorable_error'
        )


class PluginError(Exception):
    def __init__(self, reason, plugin_spec, name=None):
        self.plugin_spec = plugin_spec
        self.reason = reason
        self.name = name
    def __str__(self):
        if self.name == None:
            return '%s: %s' % (self.reason, self.plugin_spec)
        else:
            return '%s, %s: %s' % (self.plugin_spec, self.reason, self.name)


class AbstractPlugin():
    """ Common parent for all kinds of plugins, mostly to share option handling
        code. """
    def __init__(self, plugin_spec):
        self.plugin_spec = plugin_spec
        self.service_name = plugin_spec.split(':')[-1]
        self.property_prefix = '_'.join(self.service_name.lower().strip().split(' '))
        self.__property_defs = []


    def define_property(self, name, type=None, required=False, default=None):
        try:
            self.__property_defs.append((name, type, required, default))
        except AttributeError:
            raise Exception('Call AbstractPlugin.__init__ in your plugin\'s __init__.')


    def capture_properties(self, config):
        try:
            for prop in self.__property_defs:
                assert len(prop) == 4, "Property definition, %s, is invalid" % (prop,)
                self.__capture_property(config, *prop)
        except AttributeError:
            raise Exception('Call AbstractPlugin.__init__ in your plugin\'s __init__.')


    def init(self, config):
        """ This method is optional. """
        pass


    def __capture_property(self, config, name, type=None, required=False, default=None):
        """ Move a property, if present, from the ControlConfig to the daughter
            plugin. """
        config_name = '%s_%s' % (self.property_prefix, name)
        if required and not config_name in config.extra_props:
            raise PluginError(PLUGIN_ERRORS.missing_property, self.plugin_spec, config_name)

        value = default

        if config_name in config.extra_props:
            value = config.extra_props[config_name]
            del config.extra_props[config_name]

        if type != None and value != None:
            try:
                value = type(value)
            except:
                raise flashbake.ConfigError(
                        'The value, %s, for option, %s, could not be parsed as %s.'
                        % (value, name, type))
        self.__dict__[name] = value


    def abstract(self):
        """ borrowed this from Norvig
            http://norvig.com/python-iaq.html """
        import inspect
        caller = inspect.getouterframes(inspect.currentframe())[1][3]
        raise NotImplementedError('%s must be implemented in subclass' % caller)


class AbstractMessagePlugin(AbstractPlugin):
    """ Common parent class for all message plugins, will try to help enforce
        the plugin protocol at runtime. """
    def __init__(self, plugin_spec, connectable=False):
        AbstractPlugin.__init__(self, plugin_spec)
        self.connectable = connectable


    def addcontext(self, message_file, config):
        """ This method is required, it will asplode if not overridden by
            daughter classes. """
        self.abstract()


class AbstractFilePlugin(AbstractPlugin):
    """ Common parent class for all file plugins, will try to help enforce
        the plugin protocol at runtime. """
    def processfiles(self, hot_files, config):
        """ This method is required, it will asplode if not overridden by
            daughter classes. """
        self.abstract()


class AbstractNotifyPlugin(AbstractPlugin):
    """ Common parent class for all notification plugins. """
    def notify(self, hot_files, config):
        ''' Implementations will provide messages about the problem files in the
            hot_files argument through different mechanisms.
        
            N.B. This method is required, it will asplode if not overridden by
            daughter classes. '''
        self.abstract()
