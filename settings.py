# -*- coding: utf-8 -*-

import os


## note, to change logging level, change loggers['pymarc_experimentation']['level']
## see <http://stackoverflow.com/questions/17668633/what-is-the-point-of-setlevel-in-a-python-logging-handler>
LOG_CONFIG_DCT = {
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {'datefmt': '%d/%b/%Y %H:%M:%S',
        'format': '[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s'}},
    'handlers': {
        'logfile_detail': {
            'class': 'logging.FileHandler',
            'filename': os.environ['PYMARC_EXP__HANDLER_DETAIL_FILEPATH'],
            'formatter': 'standard',
            'level': 'DEBUG'},
        'logfile_error': {
            'class': 'logging.FileHandler',
            'filename': os.environ['PYMARC_EXP__HANDLER_ERROR_FILEPATH'],
            'formatter': 'standard',
            'level': 'ERROR'}
        },
    'loggers': {
        'pymarc_experimentation': {
            'handlers': ['logfile_detail', 'logfile_error'],
            'level': 'DEBUG',
            'propagate': False}
            },
    'version': 1}

INPUT_FILEPATH = os.environ['PYMARC_EXP__INPUT_MARC_FILEPATH']
OUTPUT_FILEPATH = os.environ['PYMARC_EXP__OUTPUT_MARC_FILEPATH']
