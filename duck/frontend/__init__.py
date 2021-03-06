import sys

from duck.errors import BackendError

class BaseFrontend(object):
    """
    A base class representing a Frontend.
    """

    def __init__(self, BackendClass):
        """
        A new frontend, which will be associated with a backend of the given class.
        """
        try:
            self.backend = BackendClass(self)
        except BackendError as e:
            self.handle_error(e)

    def run(self):
        raise NotImplementedError()

    def handle_error(self, e):
        """
        A default error handler: display it on stderr and exit.
        """
        sys.stderr.write('%s\n' % e)
        try:
            errcode = e.errcode
        except AttributeError:
            errcode = 1
        sys.exit(errcode)

    def async_refresh(self, changes):
        """
        Called by the backend to notify the frontend of changes in state.
        Might be called from another thread.
        """
        raise NotImplementedError()

