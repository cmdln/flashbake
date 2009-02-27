# from http://pypi.python.org/pypi/enum/
from enum import Enum
PLUGIN_ERRORS = Enum('unknown_plugin',
        'missing_attribute',
        'invalid_attribute',
        'missing_property'
        )

class PluginError(Exception):
    def __init__(self, reason, plugin_spec, name = None):
        self.plugin_spec = plugin_spec
        self.reason = reason
        self.name = name
    def __str__(self):
        if self.name == None:
            return '%s: %s' % (self.reason, self.plugin_spec)
        else:
            return '%s, %s: %s' % (self.plugin_spec, self.reason, self.name)

class AbstractMessagePlugin:
    """ Common parent class for all plugins, will try to help enforce the plugin
        protocol at runtime. """
    def __init__(self, plugin_spec, connectable = False):
        self.connectable = connectable
        self.plugin_spec = plugin_spec

    def init(self, config):
        self.__abstract()

    def addcontext(self, message_file, config):
        self.__abstract()

    def __abstract(self): 
        """ borrowed this from Norvig
            http://norvig.com/python-iaq.html """
        import inspect
        caller = inspect.getouterframes(inspect.currentframe())[1][3]
        raise NotImplementedError('%s must be implemented in subclass' % caller)

    def requireproperty(self, config, name, type = None):
        """ Useful to plugins to express a property that is required in the
            dot-control file and to move it from the extra_props dict to a
            property of the config. """
        if not name in config.extra_props:
            raise PluginError(PLUGIN_ERRORS.missing_property, name, self.plugin_spec)

        self.optionalproperty(config, name)

    def optionalproperty(self, config, name, type = None):
        """ Move a property, if present, from the ControlConfig to the daughter
            plugin. """
        value = None

        if name in config.extra_props:
            value = config.extra_props[name]
            del config.extra_props[name]

        # TODO handle ValueError
        # TODO handle bad type
        if type != None and value != None:
            value = type(value)
        self.__dict__[name] = value
