import logging
import flashbake.plugins

class MissingParent():
    def __init__(self, plugin_spec):
        pass

    def addcontext(self, message_file, control_config):
        loggin.debug('do nothing')

class NoConnectable(flashbake.plugins.AbstractMessagePlugin):
    def __init__(self, plugin_spec):
        pass

    def addcontext(self, message_file, control_config):
        loggin.debug('do nothing')

class NoAddContext(flashbake.plugins.AbstractMessagePlugin):
    def __init__(self, plugin_spec):
        flashbake.plugins.AbstractMessagePlugin.__init__(self, plugin_spec, True)

class WrongConnectable(flashbake.plugins.AbstractMessagePlugin):
    def __init__(self, plugin_spec):
        self.connectable = 1

    def addcontext(self, message_file, control_config):
        loggin.debug('do nothing')

class WrongAddContext(flashbake.plugins.AbstractMessagePlugin):
    def __init__(self, plugin_spec):
        self.connectable = True
        self.addcontext = 1
