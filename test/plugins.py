from flashbake import ControlConfig
import flashbake.plugins
import logging
import unittest



class FilesTestCase(unittest.TestCase):
    def setUp(self):
        self.config = ControlConfig()

    def testrelative(self):
        pass

class MissingParent():
    def __init__(self, plugin_spec):
        pass

    def addcontext(self, message_file, control_config):
        logging.debug('do nothing')

class NoConnectable(flashbake.plugins.AbstractMessagePlugin):
    def __init__(self, plugin_spec):
        pass

    def addcontext(self, message_file, control_config):
        logging.debug('do nothing')

class NoAddContext(flashbake.plugins.AbstractMessagePlugin):
    def __init__(self, plugin_spec):
        flashbake.plugins.AbstractMessagePlugin.__init__(self, plugin_spec, True)

class WrongConnectable(flashbake.plugins.AbstractMessagePlugin):
    def __init__(self, plugin_spec):
        self.connectable = 1

    def addcontext(self, message_file, control_config):
        logging.debug('do nothing')

class WrongAddContext(flashbake.plugins.AbstractMessagePlugin):
    def __init__(self, plugin_spec):
        self.connectable = True
        self.addcontext = 1

class Plugin1(flashbake.plugins.AbstractMessagePlugin):
    """ Sample plugin. """

    def addcontext(self, message_file, config):
        """ Stub. """
        pass

class Plugin2(flashbake.plugins.AbstractMessagePlugin):
    """ Sample plugin. """
    
    def dependencies(self):
        return ['test.plugins:Plugin1']

    def addcontext(self, message_file, config):
        """ Stub. """
        pass

class Plugin3(flashbake.plugins.AbstractMessagePlugin):
    """ Sample plugin. """
    
    def dependencies(self):
        return ['test.plugins:Plugin1', 'text.plugins:Plugin2']

    def addcontext(self, message_file, config):
        """ Stub. """
        pass
