from __future__ import absolute_import

import logging.handlers
import time

_DEFAULT_LOG_FORMAT = \
    '%(asctime)s [%(name)s][%(thread)d][%(process)d]: [%(levelname)s] %(filename)s:%(lineno)d %(message)s'


class LogConfiguration(object):
    def __init__(self, log_level=logging.ERROR, file_prefix='product_insights', file_max_size=1024, backup_count=1024,
                 formatter=logging.Formatter(_DEFAULT_LOG_FORMAT), file_handler=logging.handlers.RotatingFileHandler):
        # type: (int, str, int, int, logging.Formatter, logging.FileHandler) -> None
        self.log_level = log_level
        self.file_name = file_prefix + '.' + time.strftime("%Y-%m-%d_%H.%M") + '.log'
        self.formatter = formatter
        self.file_max_size = file_max_size
        self.backup_count = backup_count
        self.file_handler = file_handler
