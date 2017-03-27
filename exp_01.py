# -*- coding: utf-8 -*-

import datetime, json, logging, logging.config, os, pprint
import pymarc


log = logging.getLogger( 'pymarc_experimentation' )
config_dct = json.loads( os.environ['PYMARC_EXP__LOG_CONFIG_JSON'] )
config_dct['loggers']['pymarc_experimentation']['level'] = os.environ['PYMARC_EXP__LOG_LEVEL']
logging.config.dictConfig( config_dct )
log.debug( 'logging ready' )


big_marc_filepath = os.environ['PYMARC_EXP__BIG_MARC_FILEPATH']


def count_records():
    """ Counts records in marc file.
        Uses iterator so as not to have to store a huge amount of data in memory (as enclosing the reader in a list would).
        The ```utf8_handling='ignore'``` is required to avoid a unicode-error, so trapping the errant-record isn't possible this way.
        """
    with open( big_marc_filepath, 'rb' ) as fh:
        reader = pymarc.MARCReader( fh, force_utf8=True, utf8_handling='ignore' )  # w/o 'ignore', this line generates a unicode-error
        start = datetime.datetime.now()
        count = 0
        for record in reader:
            record.force_utf8 = True
            try:
                count+=1
                if count % 10000 == 0:
                    print( '`{}` records counted'.format(count) )
            except Exception as e:
                log.debug( 'exception on record ```{rec}```; error, ```{err}```'.format(rec=record, err=e) )
    end = datetime.datetime.now()
    log.debug( 'count of records in file, `{}`'.format(count) )
    log.debug( 'time_taken, `{}`'.format(end-start) )


def count_records_and_log_bad_record():
    """ Traps bad utf8 records that a for-loop can't handle.
        Under construction.
        """
    with open( big_marc_filepath, 'rb' ) as fh:
        start = datetime.datetime.now()
        count = 0
        while True:
            try:
                record = fh.readline()  # byte, not unicode-string
            except Exception as e:
                log.debug( 'exception accessing record-number ```{count}```; error, ```{err}```'.format(count=count, err=e) )
                break
            try:
                record.decode( 'utf-8' )
            except Exception as f:
                log.debug( 'exception decoding record-number ```{count}```; error, ```{err}```'.format(count=count, err=f) )
                log.debug( 'record, ```{}```'.format(record) )
                break
            count+=1
            if count % 10000 == 0:
                print( '`{}` records counted'.format(count) )
            # if count > 2:
            #     break
    end = datetime.datetime.now()
    log.debug( 'count of records in file, `{}`'.format(count) )
    log.debug( 'time_taken, `{}`'.format(end-start) )
