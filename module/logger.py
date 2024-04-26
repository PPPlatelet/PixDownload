import datetime
import logging
import os
import sys
from typing import Callable, List

import rich

"""logging.basicConfig(
    format='%(levelname)s %(asctime)s │ %(message)s',
    datefmt='%H:%M:%S.%f'
)"""

logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)s %(asctime)s line%(lineno)d| %(message)s',
                    datefmt='%Y-%m-%d %H-%M-%S'
                    )

filepath = os.getcwd() + "\\log\\%(asctime)s"
"""
def log_testing():
    logging.basicConfig(filename='log.txt',
                     format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s-%(funcName)s',
                     level=logging.ERROR)
    logging.debug('debug')
    logging.info('info')
    logging.warning('waring')
    logging.error('error')
    logging.critical('critical')
"""
if __name__ == "__main__":
    logging.debug("DEBUG")
    logging.info('INFO')
    logging.warning("WARNING")
    logging.error("ERROR")
    logging.critical("CRITICAL")
    #log_testing()