from flashbake import ControlConfig
from flashbake.plugins import PluginError
import unittest


class ConfigTestCase(unittest.TestCase):
    def setUp(self):
        self.config = ControlConfig()

    def testinvalidspec(self):
        try:
            self.config.create_plugin('test.foo')
            self.fail('Should not be able to use unknown')
        except PluginError as error:
            self.assertEqual(str(error.reason), 'invalid_plugin',
                    'Should not be able to load invalid plugin.')

    def testnoplugin(self):
        try:
            self.config.create_plugin('test.foo:Foo')
            self.fail('Should not be able to use unknown')
        except PluginError as error:
            self.assertEqual(str(error.reason), 'unknown_plugin',
                    'Should not be able to load unknown plugin.')

    def testmissingparent(self):
        try:
            plugin_name = 'test.plugins:MissingParent'
            self.config.create_plugin(plugin_name)
            self.fail(f'Should not have initialized plugin, {plugin_name}')
        except PluginError as error:
            reason = 'invalid_type'
            self.assertEqual(str(error.reason), reason,
                    f'Error should specify failure reason, {reason}.')

    def testnoconnectable(self):
        self.__testattr('test.plugins:NoConnectable', 'connectable', 'missing_attribute')

    def testwrongconnectable(self):
        self.__testattr('test.plugins:WrongConnectable', 'connectable', 'invalid_attribute')

    def testnoaddcontext(self):
        try:
            self.config.plugin_names = ['test.plugins:NoAddContext']
            from flashbake.context import buildmessagefile
            buildmessagefile(self.config)
            self.fail('Should raise a NotImplementedError.')
        except NotImplementedError:
            pass

    def testwrongaddcontext(self):
        self.__testattr('test.plugins:WrongAddContext', 'addcontext', 'invalid_attribute')

    def teststockplugins(self):
        self.config.extra_props['feed_url'] = "http://random.com/feed"

        plugins = ('flashbake.plugins.weather:Weather',
                'flashbake.plugins.uptime:UpTime',
                'flashbake.plugins.timezone:TimeZone',
                'flashbake.plugins.feed:Feed')
        for plugin_name in plugins:
            plugin = self.config.create_plugin(plugin_name)
            plugin.capture_properties(self.config)
            plugin.init(self.config)

    def testnoauthorfail(self):
        """Ensure that accessing feeds with no entry.author doesn't cause failures if the
        feed_author config property isn't set."""
        self.config.plugin_names = ['flashbake.plugins.feed:Feed']
        self.config.extra_props['feed_url'] = "http://twitter.com/statuses/user_timeline/704593.rss"
        from flashbake.context import buildmessagefile
        buildmessagefile(self.config)

    def testfeedfail(self):
        try:
            plugin = self.config.create_plugin('flashbake.plugins.feed:Feed')
            plugin.capture_properties(self.config)
            self.fail('Should not be able to initialize without full plugin props.')
        except PluginError as error:
            self.assertEqual(str(error.reason), 'missing_property',
                    'Feed plugin should fail missing property.')
            self.assertEqual(error.name, 'feed_url',
                    'Missing property should be feed.')

        self.config.extra_props['feed_url'] = "http://random.com/feed"

        try:
            plugin = self.config.create_plugin('flashbake.plugins.feed:Feed')
            plugin.capture_properties(self.config)
        except PluginError as error:
            self.fail('Should be able to initialize with just the url.')

    def __testattr(self, plugin_name, name, reason):
        try:
            plugin = self.config.create_plugin(plugin_name)
            plugin.capture_properties(self.config)
            plugin.init(self.config)
            self.fail(f'Should not have initialized plugin, {plugin_name}')
        except PluginError as error:
            self.assertEqual(str(error.reason), reason,
                    f'Error should specify failure reason, {reason}.')
            self.assertEqual(error.name, name,
                    f'Error should specify failed name, {name}')
