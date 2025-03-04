import logging
import os
from logging.handlers import RotatingFileHandler

def configuration(log_file='log/upyun.log'):
    logger = logging.getLogger('upyun')
    # 清除已有的handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [%(process)d:%(thread)d] - %(message)s')

    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # 使用RotatingFileHandler代替FileHandler
    file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)  # 文件中记录所有级别的日志

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # 将控制台输出的日志级别设置为DEBUG，这样就可以输出所有级别的日志
    console_handler.setLevel(logging.DEBUG)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger