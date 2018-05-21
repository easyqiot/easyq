from datetime import datetime
import functools


from .configuration import settings


DEBUG = 4
INFO = 3
WARNING = 2
ERROR = 1


class Logger:
    _levels = {
        DEBUG: 'DEBUG',
        INFO: 'INFO',
        WARNING: 'WARNING',
        ERROR: 'ERROR'
    }

    def __init__(self, name):
        self.name = name
        self.level = eval(settings.logging.level.upper())

    def log(self, level, msg):
        if self.level >= level:
            print(
                f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} '
                f'{self._levels[level]} {self.name} {msg}'
            )

    def error(self, msg):
        self.log(ERROR, msg)

    def warning(self, msg):
        self.log(WARNING, msg)

    def info(self, msg):
        self.log(INFO, msg)

    def debug(self, msg):
        self.log(DEBUG, msg)


class LoggerProxy(Logger):
    def __init__(self, name):
        self.name = name
        self._logger = None

    def log(self, level, msg):
        if self._logger is None:
            self._logger = Logger(self.name)
            self.log = self._logger.log
            self.log(level, msg)


loggers = {}


def getlogger(name):
    if name not in loggers:
        loggers[name] = LoggerProxy(name)

    return loggers[name]

