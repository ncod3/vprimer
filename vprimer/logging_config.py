# -*- coding: utf-8 -*-

#logger.debug('debug message')
#logger.info('info message')
#logger.warning('warn message')
#logger.error('error message')
#logger.critical('critical message')

#import os
import sys
import logging
import logging.config
from pathlib import Path

import vprimer.glv as glv
import vprimer.utils as utl


class LogConf(object):

    def __init__(self):

        self.config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'simpleFormatter': {
                    'format': \
'%(asctime)s %(levelname)s ' +
'%(module)s %(funcName)s %(lineno)s: %(message)s'
                }
            },
            'handlers': {
                'consoleHandler': {
                    'level': 'DEBUG',
                    'formatter': 'simpleFormatter',
                    'class': 'logging.StreamHandler',
                },
                'fileHandler': {
                    'level': 'DEBUG',
                    'formatter': 'simpleFormatter',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': 'no_dirname_log.txt',
                    'encoding': 'utf-8',
                }
            },
            'loggers': {
                '': {
                    'handlers': ['consoleHandler', 'fileHandler'],
                    'level': "DEBUG",
                }
            }
        }


    def logging_start(self, mod_name, out_dir_path, log_dir_path):

        log_file_path = log_dir_path / glv.log_file_name
        # save to config (str)
        self.config['handlers']['fileHandler']['filename'] = \
            str(log_file_path)
        # before logging
        utl.save_to_tmpfile(log_file_path, pre_log=True)

        log = LogConf.open_log(mod_name)

        return log


    @classmethod
    def open_log(cls, mod_name):

        # log.config dict format
        logging.config.dictConfig(glv.conf.log.config)
        log = logging.getLogger(mod_name)
        #log.info("logging start {} {}".format(mod_name, glv.conf.log.config))
        log.info("logging start {}".format(mod_name))

        return log

