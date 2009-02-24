from flashbake.plugins import AbstractPlugin

class HelloDolly(AbstractPlugin):
    """ Sample plugin. """

    def addcontext(self, message_file, config):
        """ Stub. """

        message_file.write('Hello, dolly.\n')
