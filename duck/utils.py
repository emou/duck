import datetime

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

