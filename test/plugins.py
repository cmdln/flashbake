import logging

class NoConnectable():
    def __init__(self, plugin_spec):
        pass

    def addcontext(self, message_file, control_config):
        loggin.debug('do nothing')

class NoAddContext():
    def __init__(self, plugin_spec):
        self.connectable = True


class WrongConnectable():
    def __init__(self, plugin_spec):
        self.connectable = 1

    def addcontext(seld, message_file, control_config):
        loggin.debug('do nothing')

class WrongAddContext():
    def __init__(self, plugin_spec):
        self.connectable = True
        self.addcontext = 1
