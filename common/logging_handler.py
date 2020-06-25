# -*- coding: utf-8 -*-
# @Time : 2020/5/29 20:51
# @Author : 深圳-烧烤-29期
# @File : logging_handler.py

"""日志打印"""
import logging

def get_logger(
        name='root',
        logger_level='DEBUG',
        stream_level='DEBUG',
        file_level='INFO',
        file=None,
        fmt='[%(asctime)s]--%(filename)s--%(lineno)d--%(levelname)s:%(message)s'
):
    """获取收集器"""
    logger = logging.getLogger(name)
    logger.setLevel(logger_level)
    logger.handlers.clear()
    """流输出处理器"""
    strm_handler = logging.StreamHandler()
    strm_handler.setLevel(stream_level)

    fmt = logging.Formatter(fmt)
    strm_handler.setFormatter(fmt)
    logger.addHandler(strm_handler)

    """文件输出处理器"""
    if file:
        fl_handler = logging.FileHandler(file, encoding='utf-8')
        fl_handler.setLevel(file_level)
        fl_handler.setFormatter(fmt)
        logger.addHandler(fl_handler)
    return logger
