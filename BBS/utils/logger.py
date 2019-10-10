# -*- coding: utf-8 -*-

import logging
import logging.config
import functools

from conf import LOGGING


# def write_log(func=None):
#     @functools.wraps(func)
#     def wrapper(self, *args, **kwargs):
#         name = func.__name__
#
#         gets = self.get
#         if gets:
#             logger.debug('method=%s&type=GET&content=%s', name, gets)
#         posts = self.post
#         if posts:
#             logger.debug('method=%s&type=POST&content=%s', name, posts)
#
#         res = func(self, *args, **kwargs)
#
#         try:
#             logger.debug('method=%s&type=RESPONSE&content=%s', name, res.content)
#         except Exception as e:
#             logger.debug('method=%s&type=ERROR&content=%s', name, e)
#
#         return res
#     return wrapper


def logger(name):  # 记录日志
    logging.config.dictConfig(LOGGING)
    try:
        log = logging.getLogger(name)
    except Exception as e:
        raise e

    return log
