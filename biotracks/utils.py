import logging


class NullHandler(logging.Handler):
    def emit(self, record):
        pass


class NullLogger(logging.Logger):
    def __init__(self):
        logging.Logger.__init__(self, "null")
        self.propagate = 0
        self.handlers = [NullHandler()]
