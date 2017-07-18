# #%L
# Copyright (c) 2016-2017 Cell Migration Standardisation Organization
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# #L%

import os
import errno
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


def mkdir_p(*paths):
    for p in paths:
        try:
            os.makedirs(p)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
