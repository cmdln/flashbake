from flashbake.plugins import AbstractMessagePlugin

class HelloDolly(AbstractMessagePlugin):
    """ Sample plugin. """

    def addcontext(self, message_file, config):
        """ Stub. """

        message_file.write('Hello, dolly.\n')
