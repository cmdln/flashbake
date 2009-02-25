class AbstractMessagePlugin():
    """ Common parent class for all plugins, will try to help enforce the plugin
        protocol at runtime. """
    def __init__(self):
        self.connectable = False

    def init(self, config):
        self.__abstract()

    def addcontext(self, message_file, config):
        self.__abstract()

    def __abstract(self): 
        """ borrowed this from Norvig
            http://norvig.com/python-iaq.html """
        import inspect
        caller = inspect.getouterframes(inspect.currentframe())[1][3]
        raise NotImplementedError('%s must be implemented in subclass' % caller)
