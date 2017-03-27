# -*- coding: utf-8 -*-

import datetime, json, logging, logging.config, os, pprint
import pymarc


log = logging.getLogger( 'pymarc_experimentation' )
config_dct = json.loads( os.environ['PYMARC_EXP__LOG_CONFIG_JSON'] )
config_dct['loggers']['pymarc_experimentation']['level'] = os.environ['PYMARC_EXP__LOG_LEVEL']
logging.config.dictConfig( config_dct )
log.debug( 'logging ready' )

# existing_logger_names = logging.getLogger().manager.loggerDict.keys()
# print( '- EXISTING_LOGGER_NAMES, `%s`' % existing_logger_names )
logging.getLogger('pymarc').setLevel( logging.WARNING )
logging.getLogger('TerminalIPythonApp').setLevel( logging.WARNING )


big_marc_filepath = os.environ['PYMARC_EXP__BIG_MARC_FILEPATH']


def extract_info():
    """ Prints/logs certain record elements.
        The ```utf8_handling='ignore'``` is required to avoid a unicode-error.
        """
    log.debug( 'processing file, ``{}```'.format(big_marc_filepath) )
    with open( big_marc_filepath, 'rb' ) as fh:
        reader = pymarc.MARCReader( fh, force_utf8=True, utf8_handling='ignore' )  # w/o 'ignore', this line generates a unicode-error
        start = datetime.datetime.now()
        count = 0
        for record in reader:
            record.force_utf8 = True
            record_dct = record.as_dict()
            fields = record_dct['fields']
            ##
            title = record.title()
            ##
            bib_id = 'not_available'
            item_id = 'not_available'
            record_dct_logged = False
            for field_dct in fields:
                for (k, val_dct) in field_dct.items():
                    if k == '907':
                        try:
                            bib_id = val_dct['subfields'][0]['a'][0:9]
                        except Exception as e:
                            log.debug( 'exception getting bib_id, ``{}```'.format(e) )
                            log.debug( 'record_dct, ```{}```'.format( pprint.pformat(record_dct) ) )
                            record_dct_logged = True
                    if k == '945':
                        try:
                            subfields = val_dct['subfields']
                            for subfield_dct in subfields:
                                for (k2, val2) in subfield_dct.items():
                                    if k2 == 'y':
                                        item_id = val2
                        except Exception as f:
                            log.debug( 'exception getting item_id, ``{}```'.format(f) )
                            if record_dct_logged is False:
                                log.debug( 'record_dct, ```{}```'.format( pprint.pformat(record_dct) ) )
            basic_info = {
                'title': record.title(), 'bib_id': bib_id, 'item_id': item_id }
            # print( 'bas   ic_info, ```{}```'.format( pprint.pformat(basic_info) ) )
            log.debug( 'basic_info, ```{}```'.format( pprint.pformat(basic_info) ) )
            try:
                count+=1
                if count % 10000 == 0:
                    print( '`{}` records processed'.format(count) )
                # if count > 100000:
                #     break
            except Exception as e:
                log.debug( 'exception on record ```{rec}```; error, ```{err}```'.format(rec=record, err=e) )
    end = datetime.datetime.now()
    log.debug( 'count of records in file, `{}`'.format(count) )
    log.debug( 'time_taken, `{}`'.format(end-start) )


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
