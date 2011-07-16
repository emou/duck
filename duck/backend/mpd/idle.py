from threading import Thread

from duck.log import loggers
idle_logger = loggers.idle


class IdleThread(Thread):
    """
    The thread that checks for MPD status change.
    """

    def __init__(self, backend):
        Thread.__init__(self)
        self.setDaemon(True)
        self.backend = backend
        self.frontend = self.backend.frontend
        self.should_run = True

    def run(self):
        while(self.should_run):
            self.backend._wait_for_idle()
            self.frontend.async_refresh(self.backend.last_changes())
            idle_logger.debug('woke up!')
            self.backend._idle_wokeup()

    def stop(self):
        self.should_run = False


