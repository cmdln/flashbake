import unittest
from flashbake import ControlConfig

class ConfigTestCase(unittest.TestCase):
    def setUp(self):
        self.config = ControlConfig()

    def testnoplugin(self):
        plugin = self.config.initplugin('flashbake.test.foo')

        self.assertEquals(None, plugin, 'Should not have initialized empty plugin.')

    def testnoconnectable(self):
        plugin = self.config.initplugin('flashbake.test.noconnectable')

        self.assertEquals(None, plugin, 'Should not have initialized empty plugin.')

    def testwrongconnectable(self):
        plugin = self.config.initplugin('flashbake.test.wrongconnectable')

        self.assertEquals(None, plugin, 'Should not have initialized empty plugin.')

    def teststockplugins(self):
        plugins = ('flashbake.plugins.weather',
                'flashbake.plugins.uptime',
                'flashbake.plugins.timezone',
                'flashbake.plugins.feed')
        for plugin_name in plugins:
            plugin = self.config.initplugin(plugin_name)
