from duck.backend import BackendError

class BaseFrontend(object):
    """
    A base class representing a Frontend.
    """

    def __init__(self, BackendClass):
        """
        A new frontend, which will be associated with a backend of the given class.
        """
        try:
            self.backend = BackendClass()
        except BackendError as e:
            self.handle_error(e)

    def run(self):
        raise NotImplementedError()

    def handle_error(self, e):
        """
        A default error handler: display it on stderr.
        """
        import sys
        sys.stderr.write(str(e))
