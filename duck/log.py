import logging
import settings

class LogRegistry(object):
    ''' Singleton class that holds all loggers. '''

    _loggers = {}
    _log_levels = {
        'default': logging.NOTSET,
        'debug': logging.DEBUG,
        'info': logging.INFO,
    }

    def __getattribute__(self, name):
        try:
            return LogRegistry._loggers[name]
        except KeyError:
            logger = logging.getLogger(name)
            logger.addHandler(logging.StreamHandler())
            logger.setLevel(
                LogRegistry._log_levels[
                    settings.LOG_LEVELS.get(name, 'default')
                ])
            LogRegistry._loggers[name] = logger
            return logger

loggers = LogRegistry()
