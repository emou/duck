class ErrClassSequencer(object):
    """
    A decorator that generates error-codes for each error class defined.
    """
    def __init__(self, start, step):
        self.val = start
        self.step = step

    def __call__(self, cls):
        cls.errcode = self.val
        self.val += self.step
        return cls

next_errcode = ErrClassSequencer(255, -1)

class FatalError(Exception):
    """
    An error that leads to exiting the application.
    """
    pass

@next_errcode
class BackendError(FatalError):
    """
    A base error in the backend.
    """
    pass

@next_errcode
class BackendInitializeError(BackendError):
    """
    An error during backend initialization, i.e.
    could not connect to server, could not import
    a module, etc.
    """
    pass

@next_errcode
class BackendConnectionError(BackendError):
    """
    An error while connecting to the backend.
    """
    pass

@next_errcode
class FrontendError(FatalError):
    """
    A base error in the frontend.
    """
    pass

@next_errcode
class FrontendInitializeError(FrontendError):
    """
    An error during frontend initialization, i.e.
    could not initialize the GUI, could not import
    a module, etc.
    """
    pass
