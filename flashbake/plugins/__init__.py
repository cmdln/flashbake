# from http://pypi.python.org/pypi/enum/
from enum import Enum
PLUGIN_ERRORS = Enum('unknown_plugin',
        'missing_attribute',
        'invalid_attribute',
        'missing_property'
        )

class PluginError(Exception):
    def __init__(self, reason, name, plugin_spec = None):
        self.plugin_spec = plugin_spec
        self.reason = reason
        self.name = name
    def __str__(self):
        if self.plugin_spec == None:
            return '%s: %s' % (self.reason, self.name)
        else:
            return '%s - %s: %s' % (self.plugin_spec, self.reason, self.name)
            :
class AbstractMessagePlugin():
    """ Common parent class for all plugins, will try to help enforce the plugin
        protocol at runtime. """
    def __init__(self):
        self.connectable = False

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
