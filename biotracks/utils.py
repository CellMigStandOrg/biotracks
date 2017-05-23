# #%L
# #L%

import logging


LOG_LEVELS = frozenset([
    'CRITICAL',
    'DEBUG',
    'ERROR',
    'FATAL',
    'INFO',
    'NOTSET',
    'WARN',
    'WARNING',
])
LOG_FORMAT = '%(asctime)s %(levelname)s: [%(name)s] %(message)s'


class NullHandler(logging.Handler):
    def emit(self, record):
        pass


class NullLogger(logging.Logger):
    def __init__(self):
        logging.Logger.__init__(self, "null")
        self.propagate = 0
        self.handlers = [NullHandler()]


def get_log_level(s):
    try:
        return int(s)
    except ValueError:
        level_name = s.upper()
        if level_name in LOG_LEVELS:
            return getattr(logging, level_name)
        else:
            raise ValueError('%r is not a valid log level' % (s,))


def get_logger(name, level=None, f=None, mode='a'):
    if level is None:
        return NullLogger()
    logger = logging.getLogger(name)
    logger.setLevel(get_log_level(level))
    if isinstance(f, str):
        handler = logging.FileHandler(f, mode=mode)
    else:
        handler = logging.StreamHandler(f)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(handler)
    return logger
