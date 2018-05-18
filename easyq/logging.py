from datetime import datetime
import functools


INFO = 3
WARNING = 2
ERROR = 1


class Logger:
    _levels = {
        INFO: 'INFO',
        WARNING: 'WARNING',
        ERROR: 'ERROR'
    }

    def __init__(self, name):
        self.name = name

    def log(self, level, msg):
        print(
            f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} '
            f'{self._levels[level]} {self.name.upper()} {msg}'
        )

    def error(self, msg):
        self.log(ERROR, msg)

    def warning(self, msg):
        self.log(WARNING, msg)

    def info(self, msg):
        self.log(INFO, msg)


loggers = {}


def get_logger(name):
    if name not in loggers:
        loggers[name] = Logger(name)

    return loggers[name]

