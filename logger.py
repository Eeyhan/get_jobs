#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  : Eeyhan
# @File    : logger.py

import logging
from config import BASE_DIR, LOG_NAME, LOG_LEVEL


def logger():
    # 创建一个文件型日志对象
    log_file = '%s/log/%s' % (BASE_DIR, LOG_NAME)
    fh = logging.FileHandler(log_file)
    fh.setLevel(LOG_LEVEL)

    # 设置日志格式
    formater = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 添加格式到文件型和输出型日志对象中
    fh.setFormatter(formater)

    # 创建log对象，命名
    logger = logging.getLogger(LOG_NAME)
    logger.setLevel(LOG_LEVEL)

    # 把文件型日志和输出型日志对象添加进logger
    logger.addHandler(fh)

    return logger
