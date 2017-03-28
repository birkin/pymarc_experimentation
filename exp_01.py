# -*- coding: utf-8 -*-

import datetime, json, logging, logging.config, os, pprint
import pymarc


log = logging.getLogger( 'pymarc_experimentation' )
config_dct = json.loads( os.environ['PYMARC_EXP__LOG_CONFIG_JSON'] )
logging.config.dictConfig( config_dct )
log.debug( 'logging ready' )

# existing_logger_names = logging.getLogger().manager.loggerDict.keys()
# print( '- EXISTING_LOGGER_NAMES, `%s`' % existing_logger_names )
logging.getLogger('pymarc').setLevel( logging.WARNING )
logging.getLogger('TerminalIPythonApp').setLevel( logging.WARNING )


big_marc_filepath = os.environ['PYMARC_EXP__BIG_MARC_FILEPATH']


class Extractor( object ):
    """ Manages extraction of info from records in a marc file. """

    def __init__( self ):
        self.marc_filepath = os.environ['PYMARC_EXP__BIG_MARC_FILEPATH']
        log.debug( 'processing file, ``{}```'.format(self.marc_filepath) )
        self.count = 0
        self.title = 'not_available'
        self.bib_id = 'not_available'
        self.item_id = 'not_available'
        self.record_dct_logged = False

    def extract_info( self ):
        """ Prints/logs certain record elements.
            The ```utf8_handling='ignore'``` is required to avoid a unicode-error.
            """
        start = datetime.datetime.now()
        with open( self.marc_filepath, 'rb' ) as fh:
            reader = pymarc.MARCReader( fh, force_utf8=True, utf8_handling='ignore' )  # w/o 'ignore', this line generates a unicode-error
            for record in reader:
                ( fields, record_dct ) = self.setup_main_loop( record )
                for field_dct in fields:
                    self.find_bib_and_item( field_dct, record_dct )
                self.log_basic_info()
                self.update_count()
                # if count > 3: break
        log.info( 'count of records in file, `{count}`; time_taken, `{time}`'.format( count=self.count, time=datetime.datetime.now()-start ) )

    def setup_main_loop( self, record ):
        """ Initializes main processing loop.
            Called by extract_info() """
        self.title = record.title()
        self.bib_id = 'not_available'
        self.item_id = 'not_available'
        self.record_dct_logged = False
        record.force_utf8 = True
        record_dct = record.as_dict()
        fields = record_dct['fields']
        return_tpl = ( fields, record_dct )
        log.debug( 'return_tpl ( fields, record_dct ), ```{}```'.format(return_tpl) )
        return return_tpl

    def find_bib_and_item( self, field_dct, record_dct ):
        """ Extracts bib_id and item_id.
            Called by extract_info() """
        for (k, val_dct) in field_dct.items():
            log.debug( 'k, `{k}`; val_dct, ```{v}```'.format( k=k, v=pprint.pformat(val_dct) ) )
            self.extract_bib( k, val_dct, record_dct )
            self.extract_item( k, val_dct, record_dct )
        return

    def extract_bib( self, k, val_dct, record_dct ):
        """ Checks for bib.
            Called by find_bib_and_item() """
        if k == '907':
            try:
                self.bib_id = val_dct['subfields'][0]['a'][0:9]
            except Exception as e:
                log.debug( 'exception getting bib_id, ``{}```'.format(e) )
                log.debug( 'record_dct, ```{}```'.format( pprint.pformat(record_dct) ) )
                self.record_dct_logged = True
        return

    def extract_item( self, k, val_dct, record_dct ):
        """ Checks for item_id.
            Called by find_bib_and_item() """
        if k == '945':
            try:
                subfields = val_dct['subfields']
                for subfield_dct in subfields:
                    for (k2, val2) in subfield_dct.items():
                        if k2 == 'y':
                            self.item_id = val2
            except Exception as f:
                log.debug( 'exception getting item_id, ``{}```'.format(f) )
                if self.record_dct_logged is False:
                    log.debug( 'record_dct, ```{}```'.format( pprint.pformat(record_dct) ) )
        return

    def log_basic_info( self ):
        """ Assembles & logs extracted info.
            Called by extract_info() """
        basic_info = { 'title': self.title, 'bib_id': self.bib_id, 'item_id': self.item_id }
        log.info( 'basic_info, ```{}```'.format( pprint.pformat(basic_info) ) )
        return

    def update_count( self ):
        """ Updates count and process-reporting.
            Called by extract_info() """
        self.count+=1
        if self.count % 10000 == 0:
            print( '`{}` records processed'.format(self.count) )
        return

    ## end class Extractor()




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
