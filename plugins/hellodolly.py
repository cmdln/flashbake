from flashbake import AbstractPlugin

class HelloDolly(AbstractPlugin):

    def addcontext(self, message_file, config):
        """ Stub. """

        message_file.write('Hello, dolly.')
