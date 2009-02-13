import unittest
from flashbake import ControlConfig, PluginError

class ConfigTestCase(unittest.TestCase):
    def setUp(self):
        self.config = ControlConfig()
        self.config.extra_props['feed'] = "http://random.com/feed"
        self.config.extra_props['author'] = "Joe Random"
        self.config.extra_props['limit'] = "3"

    def testnoplugin(self):
        try:
            plugin = self.config.initplugin('flashbake.test.foo')
            self.fail('Should not be able to use unknown')
        except PluginError, error:
            self.assertEquals(str(error.reason), 'unknown_plugin',
                    'Should not be able to load unknown plugin.')

    def testnoconnectable(self):
        self.__testattr('flashbake.test.noconnectable', 'connectable', 'missing_attribute')

    def testwrongconnectable(self):
        self.__testattr('flashbake.test.wrongconnectable', 'connectable', 'invalid_attribute')

    def testnoaddcontext(self):
        self.__testattr('flashbake.test.noaddcontext', 'addcontext', 'missing_attribute')

    def testwrongaddcontext(self):
        self.__testattr('flashbake.test.wrongaddcontext', 'addcontext', 'invalid_attribute')

    def teststockplugins(self):
        plugins = ('flashbake.plugins.weather',
                'flashbake.plugins.uptime',
                'flashbake.plugins.timezone',
                'flashbake.plugins.feed')
        for plugin_name in plugins:
            plugin = self.config.initplugin(plugin_name)

    def __testattr(self, plugin_name, name, reason):
        try:
            plugin = self.config.initplugin(plugin_name)
            self.fail('Should not have initialized plugin, %s', plugin_name)
        except PluginError, error:
            self.assertEquals(str(error.reason), reason,
                    'Error should specify failure reason, %s.' % reason)
            self.assertEquals(error.name, name,
                    'Error should specify failed name, %s' % name)
