# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime, json, logging, logging.config, os, pprint, sys, traceback
import pymarc


log = logging.getLogger( 'pymarc_experimentation' )
config_dct = json.loads( os.environ['PYMARC_EXP__LOG_CONFIG_JSON'] )
logging.config.dictConfig( config_dct )
log.debug( 'logging ready' )

# existing_logger_names = logging.getLogger().manager.loggerDict.keys()
# print( '- EXISTING_LOGGER_NAMES, `%s`' % existing_logger_names )
logging.getLogger('pymarc').setLevel( logging.WARNING )
logging.getLogger('TerminalIPythonApp').setLevel( logging.WARNING )


class Extractor( object ):
    """ Manages extraction of info from records in a marc file. """

    def __init__( self ):
        self.marc_filepath = os.environ['PYMARC_EXP__BIG_MARC_FILEPATH']
        log.debug( 'processing file, ``{}```'.format(self.marc_filepath) )
        self.count = 0
        self.title = 'init'
        self.bib_id = 'init'
        self.item_id = 'init'
        self.record_dct = 'init'
        self.record_dct_logged = False

    def extract_info( self ):
        """ Prints/logs certain record elements.
            The ```utf8_handling='ignore'``` is required to avoid a unicode-error.
            """
        start = datetime.datetime.now()
        with open( self.marc_filepath, 'rb' ) as fh:
            reader = pymarc.MARCReader( fh, force_utf8=True, utf8_handling='ignore' )  # w/o 'ignore', this line generates a unicode-error
            for record in reader:
                self.setup_main_loop( record )  # updates instance vars
                for field_dct in self.record_dct['fields']:
                    self.find_bib_and_item( field_dct )
                self.log_basic_info()
                self.update_count()
                # if count > 3: break
        log.info( 'count of records in file, `{count}`; time_taken, `{time}`'.format( count=self.count, time=datetime.datetime.now()-start ) )

    def setup_main_loop( self, record ):
        """ Initializes main processing loop.
            Called by extract_info() """
        record.force_utf8 = True
        self.title = record.title()
        self.bib_id = 'not_available'
        self.item_id = 'not_available'
        self.record_dct_logged = False
        self.record_dct = record.as_dict()
        log.debug( 'self.record_dct, ```{}```'.format(self.record_dct) )
        return

    def find_bib_and_item( self, field_dct ):
        """ Extracts bib_id and item_id.
            Called by extract_info() """
        for (k, val_dct) in field_dct.items():
            log.debug( 'k, `{k}`; val_dct, ```{v}```'.format( k=k, v=pprint.pformat(val_dct) ) )
            self.extract_bib( k, val_dct )
            self.extract_item( k, val_dct )
        return

    def extract_bib( self, k, val_dct ):
        """ Checks for bib.
            Called by find_bib_and_item() """
        if k == '907':
            try:
                self.bib_id = val_dct['subfields'][0]['a'][0:9]
            except Exception as e:
                log.debug( 'exception getting bib_id, ``{}```'.format(e) )
                log.debug( 'record_dct, ```{}```'.format( pprint.pformat(self.record_dct) ) )
                self.record_dct_logged = True
        return

    def extract_item( self, k, val_dct ):
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
                    log.debug( 'record_dct, ```{}```'.format( pprint.pformat(self.record_dct) ) )
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


#####################################
## experimentation functions below ##
#####################################


def break_up_record( start_record=0, end_record=0 ):
    """ Splits big marc file into smaller files.
        This can successfully re-write the whole errant `rec_19.mrc` file. """
    log.debug( 'start_record, `{st}`; end_record, `{en}`'.format( st=start_record, en=end_record ) )
    BIG_MARC_FILEPATH = os.environ['PYMARC_EXP__BIG_MARC_FILEPATH']
    SMALLER_OUTPUT_FILEPATH = os.environ['PYMARC_EXP__SMALLER_OUTPUT_MARC_FILEPATH']
    log.debug( 'processing file, ``{}```'.format(BIG_MARC_FILEPATH) )
    log.debug( 'output file, ``{}```'.format(SMALLER_OUTPUT_FILEPATH) )

    start_time = datetime.datetime.now()
    count = 0
    last_record = 'init'

    with open( BIG_MARC_FILEPATH, 'rb' ) as input_fh:
        # reader = pymarc.MARCReader( input_fh, force_utf8=True, utf8_handling='ignore' )
        # reader = pymarc.MARCReader( input_fh )
        # reader = pymarc.MARCReader( input_fh, to_unicode=True )

        # reader = pymarc.MARCReader( input_fh, to_unicode=True, utf8_handling='ignore' )  # works!
        reader = pymarc.MARCReader( input_fh, to_unicode=True, force_utf8=True, utf8_handling='ignore' )
        # reader = pymarc.MARCReader( input_fh, to_unicode=False, utf8_handling='ignore' )

        with open( SMALLER_OUTPUT_FILEPATH, 'wb' ) as output_fh:
            writer = pymarc.MARCWriter( output_fh )


            processing_flag = True
            while processing_flag is True:
                try:
                    record = next(reader)
                except Exception as e:
                    record = None
                    log.error( 'exception looping through records; ```{}```'.format( unicode(repr(e)) ) )
                    log.error( 'e info, ```{}```'.format(e) )
                    e_type, e_value, e_traceback = sys.exc_info()  # <http://stackoverflow.com/a/15890953>
                    log.error( 'e_type, ```{}``'.format(e_type) )
                    log.error( 'e_value, ```{}``'.format(e_value) )
                    log.error( 'e_traceback, ```{}```'.format(e_traceback) )
                    log.error( 'traceback info, ```{}```'.format( traceback.format_exc() ) )
                    # log.error( 'current record, ```{}```'.format( record ) )
                    log.error( 'current count, `{}`'.format(count) )
                    # log.error( 'last_record, ```{}```'.format(last_record) )

                last_record = record
                count += 1
                if count % 10000 == 0:
                    print( '`{}` records processed'.format(count) )
                if count >= start_record:
                    log.debug( 'count, `{}`'.format(count) )
                    if record:
                        log.debug( 'count is, `{cnt}`, so will write record.as_json()[0:100], ```{rcd}```'.format( cnt=count, rcd=record.as_json()[0:100] ) )
                        writer.write( record )
                    if count >= end_record:
                        processing_flag = False


    end_time = datetime.datetime.now()
    log.debug( 'records processed, `{}`'.format(count) )
    log.debug( 'time_taken, `{}`'.format(end_time-start_time) )

    ## end def break_up_record()


# def break_up_record( start_record=0, end_record=0 ):
#     """ Splits big marc file into smaller files.
#         This can successfully re-write the whole errant `rec_19.mrc` file. """
#     log.debug( 'start_record, `{st}`; end_record, `{en}`'.format( st=start_record, en=end_record ) )
#     BIG_MARC_FILEPATH = os.environ['PYMARC_EXP__BIG_MARC_FILEPATH']
#     SMALLER_OUTPUT_FILEPATH = os.environ['PYMARC_EXP__SMALLER_OUTPUT_MARC_FILEPATH']
#     log.debug( 'processing file, ``{}```'.format(BIG_MARC_FILEPATH) )
#     log.debug( 'output file, ``{}```'.format(SMALLER_OUTPUT_FILEPATH) )

#     start_time = datetime.datetime.now()
#     count = 0

#     with open( BIG_MARC_FILEPATH, 'rb' ) as input_fh:
#         # reader = pymarc.MARCReader( input_fh, force_utf8=True, utf8_handling='ignore' )
#         # reader = pymarc.MARCReader( input_fh )
#         # reader = pymarc.MARCReader( input_fh, to_unicode=True )
#         reader = pymarc.MARCReader( input_fh, to_unicode=True, utf8_handling='ignore' )  # works!

#         with open( SMALLER_OUTPUT_FILEPATH, 'wb' ) as output_fh:
#             writer = pymarc.MARCWriter( output_fh )

#             for record in reader:
#                 count += 1
#                 if count % 10000 == 0:
#                     print( '`{}` records processed'.format(count) )
#                 if count >= start_record:
#                     writer.write( record )
#                     if count >= end_record:
#                         break

#     end_time = datetime.datetime.now()
#     log.debug( 'records processed, `{}`'.format(count) )
#     log.debug( 'time_taken, `{}`'.format(end_time-start_time) )

#     ## end def break_up_record()


def extract_info():
    """ Prints/logs certain record elements.
        The ```utf8_handling='ignore'``` is required to avoid a unicode-error.
        """
    big_marc_filepath = os.environ['PYMARC_EXP__BIG_MARC_FILEPATH']
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
            log.info( 'basic_info, ```{}```'.format( pprint.pformat(basic_info) ) )
            try:
                count+=1
                if count % 10000 == 0:
                    print( '`{}` records processed'.format(count) )
                # if count > 100000:
                #     break
            except Exception as e:
                log.debug( 'exception on record ```{rec}```; error, ```{err}```'.format(rec=record, err=e) )
    end = datetime.datetime.now()
    log.info( 'count of records in file, `{}`'.format(count) )
    log.info( 'time_taken, `{}`'.format(end-start) )

    ## end def extract_info()


def count_records():
    """ Counts records in marc file.
        Uses iterator so as not to have to store a huge amount of data in memory (as enclosing the reader in a list would).
        The ```utf8_handling='ignore'``` is required to avoid a unicode-error, so trapping the errant-record isn't possible this way.
        """
    big_marc_filepath = os.environ['PYMARC_EXP__BIG_MARC_FILEPATH']
    with open( big_marc_filepath, 'rb' ) as fh:
        reader = pymarc.MARCReader( fh, force_utf8=True, utf8_handling='ignore' )  # w/o 'ignore', this line can generate a unicode-error
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
        <https://github.com/edsu/pymarc/blob/master/test/reader.py>
        Under construction.
        """
    big_marc_filepath = os.environ['PYMARC_EXP__BIG_MARC_FILEPATH']
    with open( big_marc_filepath, 'rb' ) as fh:
        start = datetime.datetime.now()
        count = 0

        reader = pymarc.MARCReader( fh, to_unicode=True, force_utf8=True, utf8_handling='ignore' )

        last_record = 'init'
        start_offset = 0
        end_offset = 0
        capture_flag = False  # for capturing problematic marc-records as strings
        problem_string = 'init'
        processing_flag = True
        while processing_flag:
            try:
                start_offset = fh.tell()
                record = next( reader )
                end_offset = fh.tell()
                last_record = record
            except Exception as e:
                log.error( 'exception looping through records; ```{}```'.format( unicode(repr(e)) ) )
                log.error( 'count, `{}`'.format(count) )
                if last_record:
                    log.error( 'last_record.as_json()[0:500], ```{}```'.format( last_record.as_json()[0:500] ) )
                last_record = None
                log.debug( 'error start_offset, `{}`'.format(start_offset) )
                log.debug( 'error end_offset, `{}`'.format(end_offset) )
            count+=1
            if count % 10000 == 0:
                print( '`{}` records counted'.format(count) )
            if count > 81219:
                log.debug( 'start_offset, `{}`'.format(start_offset) )
                log.debug( 'end_offset, `{}`'.format(end_offset) )
                if start_offset == end_offset:  # means there was a problem
                    capture_flag = True
                if ( end_offset > start_offset ) and capture_flag is True:
                    capture_flag = False
                    bytes_to_read = end_offset - start_offset
                    with open( big_marc_filepath, 'rb' ) as error_file_handler:
                        error_file_handler.seek( start_offset )
                        problem_string = error_file_handler.read( bytes_to_read )
                        log.debug( 'type(problem_string), `{}`'.format(type(problem_string)) )
                        u_problem_string = problem_string.decode( 'utf-8' )
                        log.warning( 'problem_string, ```{}```'.format(u_problem_string) )

            if count > 81222:
                processing_flag = False
    end = datetime.datetime.now()
    log.debug( 'count of records in file, `{}`'.format(count) )
    log.debug( 'time_taken, `{}`'.format(end-start) )


# def count_records_and_log_bad_record():
#     """ Traps bad utf8 records that a for-loop can't handle.
#         Under construction.
#         """
#     big_marc_filepath = os.environ['PYMARC_EXP__BIG_MARC_FILEPATH']
#     with open( big_marc_filepath, 'rb' ) as fh:
#         start = datetime.datetime.now()
#         count = 0
#         while True:
#             try:
#                 record = fh.readline()  # byte, not unicode-string
#             except Exception as e:
#                 log.debug( 'exception accessing record-number ```{count}```; error, ```{err}```'.format(count=count, err=e) )
#                 continue
#             try:
#                 record.decode( 'utf-8' )
#             except Exception as f:
#                 log.debug( 'exception decoding record-number ```{count}```; error, ```{err}```'.format(count=count, err=f) )
#                 log.debug( 'record, ```{}```'.format(record) )
#                 continue
#             count+=1
#             if count % 10000 == 0:
#                 print( '`{}` records counted'.format(count) )
#             # if count > 2:
#             #     break
#     end = datetime.datetime.now()
#     log.debug( 'count of records in file, `{}`'.format(count) )
#     log.debug( 'time_taken, `{}`'.format(end-start) )
