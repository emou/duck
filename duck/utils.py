import datetime
import threading
import time


class Calculations(object):

    @staticmethod
    def percent(n, x):
        """
        Returns n percent of x.
        """
        assert(100 >= n >= 0)
        assert(x >= 0)
        return (n * x / 100.0)

    @staticmethod
    def intpercent(n, x):
        """
        Returns a round of n percent of x.
        """
        assert(100 >= n >= 0)
        assert(x >= 0)
        return (n * x) / 100


class Duration(datetime.timedelta):
    """
    Timedelta with better formatting and ... a properly capitalized class name.
    """
    def __str__(self):
        try:
            # timedelta objects are immutable, so we might as well memoize the
            # result
            return self.fmt
        except AttributeError:
            seconds = self.total_seconds()
            (minutes, seconds) = divmod(seconds, 60)
            (hours, minutes) = divmod(minutes, 60)

            if hours:
                self.fmt = '%d:%02d:%02d' % (hours, minutes, seconds)
            else:
                self.fmt = '%d:%02d' % (minutes, seconds)
            return self.fmt


class Poller(threading.Thread):
    """
    A thread that polls a given function until it sucessfully finishes.
    """

    @staticmethod
    def default_sleep_generator():
        yield 0
        while True:
            s = 1
            for x in range(5):
                yield s
                s *= 2


    def __init__(self,
                 try_func,
                 success_handler = lambda: None,
                 exception_handler = lambda: None,
                 sleep_generator = None,
                ):
        """
        Parameters:
            try_func: the function to poll
            success_handler: called on success with the return value of
            try_func as an argument
            exception_handler: called on exception
            sleep_generator: a generator that determines sleep interval change
        """
        threading.Thread.__init__(self)
        self.setDaemon(True)

        self.try_func = try_func
        self.success_handler = success_handler
        self.exception_handler = exception_handler
        self.sleep_generator = sleep_generator or Poller.default_sleep_generator()

        self.need_try = threading.Event()
        self.need_try.set()

    def run(self):
        """
        Main thread loop. Polls the function until success. After one succeeded
        call, you need to call `kick` to start polling again.
        """
        while True:
            time.sleep(self.sleep_generator.next())
            self.need_try.wait()
            try:
                res = self.try_func()
            except Exception, e:
                self.exception_handler(e)
            else:
                self.success_handler(res)
                self.need_try.clear()

    def kick(self):
        """
        Restart the polling. Has no effect if already polling.
        """
        self._need_try.set()

