import unittest
from flashbake import ControlConfig, PluginError

class ConfigTestCase(unittest.TestCase):
    def setUp(self):
        self.config = ControlConfig()

    def testnoplugin(self):
        try:
            plugin = self.config.initplugin('test.foo')
            self.fail('Should not be able to use unknown')
        except PluginError, error:
            self.assertEquals(str(error.reason), 'unknown_plugin',
                    'Should not be able to load unknown plugin.')

    def testnoconnectable(self):
        self.__testattr('test.noconnectable', 'connectable', 'missing_attribute')

    def testwrongconnectable(self):
        self.__testattr('test.wrongconnectable', 'connectable', 'invalid_attribute')

    def testnoaddcontext(self):
        self.__testattr('test.noaddcontext', 'addcontext', 'missing_attribute')

    def testwrongaddcontext(self):
        self.__testattr('test.wrongaddcontext', 'addcontext', 'invalid_attribute')

    def teststockplugins(self):
        self.config.extra_props['feed'] = "http://random.com/feed"
        self.config.extra_props['author'] = "Joe Random"
        self.config.extra_props['limit'] = "3"

        plugins = ('flashbake.plugins.weather',
                'flashbake.plugins.uptime',
                'flashbake.plugins.timezone',
                'flashbake.plugins.feed')
        for plugin_name in plugins:
            plugin = self.config.initplugin(plugin_name)

    def testfeedfail(self):
        try:
            self.config.initplugin('flashbake.plugins.feed')
            self.fail('Should not be able to initialize without full plugin props.')
        except PluginError, error:
            self.assertEquals(str(error.reason), 'missing_property',
                    'Feed plugin should fail missing property.')
            self.assertEquals(error.name, 'feed',
                    'Missing property should be feed.')

        self.config.extra_props['feed'] = "http://random.com/feed"

        try:
            self.config.initplugin('flashbake.plugins.feed')
            self.fail('Should not be able to initialize without full plugin props.')
        except PluginError, error:
            self.assertEquals(str(error.reason), 'missing_property',
                    'Feed plugin should fail missing property.')
            self.assertEquals(error.name, 'author',
                    'Missing property should be author.')

        self.config.extra_props['feed'] = "http://random.com/feed"
        self.config.extra_props['author'] = "Joe Random"

        try:
            self.config.initplugin('flashbake.plugins.feed')
            self.fail('Should not be able to initialize without full plugin props.')
        except PluginError, error:
            self.assertEquals(str(error.reason), 'missing_property',
                    'Feed plugin should fail missing property.')
            self.assertEquals(error.name, 'limit',
                    'Missing property should be limit.')

    def __testattr(self, plugin_name, name, reason):
        try:
            plugin = self.config.initplugin(plugin_name)
            self.fail('Should not have initialized plugin, %s', plugin_name)
        except PluginError, error:
            self.assertEquals(str(error.reason), reason,
                    'Error should specify failure reason, %s.' % reason)
            self.assertEquals(error.name, name,
                    'Error should specify failed name, %s' % name)