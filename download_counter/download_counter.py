#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Download counter
================

Reads access.log and looks for files with specified file extensions, which are
then logged in the download stats database (SQLite).


Usage
=====

The main functional parameters are set in download_counter.cfg.
Additional options may be set through command line arguments.


Command line switches
---------------------

usage: download_counter.py [-d] [-h] [-i] [-v] [-V]

Arguments:

-d, --docs
    show this documentation and exit.

-h, --help
    Show short help and exit.

-i, --init string
    This option is required if you wish to count downloads in old
    archived '.gz' files.

    All access logs in path, (including .gz files), are read.
    Matching download files are counted regardless of when they were
    downloaded, so this option should only be used on first run, (before
    the database contains data). This option overrides ACCESSLOGS in
    download_counter.cfg.

Example
-------
The path string should be entered in the form::

    $ python3 download-counter -n '/var/log/nginx/access.log'

To read all logs::

    * /var/log/nginx/access.log
    * /var/log/nginx/access.log.1
    * /var/log/nginx/access.log.2.gz
    * /var/log/nginx/access.log.3.gz
    * ...

-v, --verbose
    print commands and database contents to standard output.

-V, --version
    show program version and exit.


Configuration file
------------------

The configuration file ('download_counter.cfg') must be in the same
directory as 'download_counter.py'.

The cfg file contains 5 sections:

**ACCESSLOGS:** One or more access logs.

    Log files must be plain text (NOT .gz archives).
    When more than one access.log files specified, files must be in
    reverse chronological order (process oldest first).

    Default:
        - log1 = /var/log/nginx/access.log.1
        - log2 = /var/log/nginx/access.log

**SQLITE:** Absolute or relative path to database.

    By default the database will be in the same folder as
    download_counter.py

    Default:
        path = downloads.db

**FILEPATH:** The first part of the download file's string.

    This refers to the string as it appears in the access log.
    If not supplied, all file names matching the FILENAMES
    option(s) will be counted.

    Default:
        path = /wp-content/uploads/

    The default option will catch files in any of:

        * .../website/downloads/2001/
        * .../website/downloads/2002/
        * .../website/downloads/.../

**FILENAMES:** Download files end of string.

    The default options will catch .zip and .exe files that begin with
    'FILEPATH'.

    Default:
        - file1 = .zip
        - file2 = .exe


**WEBPAGE:** Absolute or relative path to html output.

    HTML output is disabled if this path is not specified.

    Default:
        path = /var/www/html/downloads.html

Note:
-----

    FILEPATH and FILENAMES options are just strings that will be searched for
    in the accesslog file(s). Regex is used to search the log file(s) for:
    "<path-string> any-characters <file-string>"

"""


import sys
import sqlite3
import argparse
import configparser
import re
import gzip

from datetime import datetime
from glob import iglob

import download_counter_html as htm


def default_date_time_format():
    """Return the date-time format of access.log

    Modify this string if necessary to match the date-time string in the
    access logs.

    Returns
    -------
    string
        datetime format string.

    """
    return '%d/%b/%Y:%H:%M:%S %z'


def print_table(dbase):
    """Print contents of downloads in 'dbase' to standard out.

    This function is used only with --verbose option.

    Parameters
    ----------
    dbase : string
        Path to SQLite database.

    Returns
    -------
    None

    """
    sql_get_table = 'SELECT * FROM downloads'
    print('\nID \tFile \t\t Timestamp \t\t Total')
    try:
        conn = sqlite3.connect(dbase)
        with conn:
            records = conn.execute(sql_get_table)
            for row in records:
                for val in row:
                    print(val, end='\t')
                print('')
    except sqlite3.OperationalError as err:
        sys.exit(err)
    conn.close()


def get_db_time(con):
    """Return most recent timestamp from database.

    Parameters
    ----------
    con : connection
        Connection to the database.

    Returns
    -------
    datetime
        datetime.min if timestamp not found.

    """
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    try:
        cur.execute('select timestamp from downloads')
    except sqlite3.OperationalError as err:
        print(err)
    recent = datetime.min
    for row in cur:
        if row['timestamp'] > recent:
            recent = row['timestamp']
    return recent


def sql_table(con):
    """ Create 'downloads' table if it doesn't exist.

    Parameters
    ----------
    con : connection
        Connection to the database.

    Returns
    -------
    None

    """
    cursor = con.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS downloads (
                                id INTEGER PRIMARY KEY,
                                filename TEXT NOT NULL UNIQUE,
                                timestamp TIMESTAMP NOT NULL,
                                total INTEGER DEFAULT 0);''')
    con.commit()


def get_record(record, pattern):
    """Return (filename, time) from line when start
    and end of name are found, or None if not found.

    Parameters
    ----------
    record : string
        One line from access log.
    pattern : string
        Regex pattern:
        f'GET {re.escape(start)}.*{re.escape(end)}'

    Returns
    -------
    tuple
        (Short filename string, datetime object) if successful,or None.

    """
    found = re.search(pattern, record)
    # HTTP response status code is after the first
    # quoted string in record.
    pattern = r'"(.+?)"(\s\d{3}){1}'
    if found:
        filename = found[0].split('/')[-1]
        response = re.search(pattern, record).group()
        if re.search('200$', response):
            return (filename, get_time(record))
    return None


def get_time(record):
    """Return timestamp from record.

    Parameters
    ----------
    record : string

    Returns
    -------
    datetime
        Exit if timestamp not found.

    """
    time_string = re.search(r"\[.*\]", record)
    if time_string:
        _logtime = (time_string[0].strip('[]'))
        try:
            _timestamp = datetime.strptime(_logtime,
                                           default_date_time_format())
            return _timestamp.replace(tzinfo=None)
        except ValueError as err:
            sys.exit(err)
    else:
        sys.exit('Could not read timestamp from log.')


def update_db(con, fname, timestamp):
    """Update database.

    If fname exists in database, update its download total and timestamp,
    else insert it into the database with a count of 1.

    Parameters
    ----------
    con : connection
        Connection to the database.
    fname : string
        Name of the downloaded file.
    timestamp : datetime
        Timestamp of download.

    Returns
    -------
    None

    """
    cursor = con.cursor()
    timestamp_query = 'Update downloads set timestamp = ? where filename = ?'
    counter_query = 'Update downloads set total = total + 1 where filename = ?'
    insert_query = """INSERT OR IGNORE INTO downloads
                   (filename, timestamp, total)
                   VALUES (?, ?, ?)"""
    cursor.execute(timestamp_query, (timestamp, fname))
    cursor.execute(counter_query, (fname,))
    cursor.execute(insert_query, (fname, timestamp, 1))
    con.commit()
    cursor.close()


def write_html(con, htmlfile):
    """Write sql data to web page.

    Parameters
    ----------
    con : connection
        Connection to the database.
    htmlfile : string
        Path to html output file.

    Returns
    -------
    None

    """
    try:
        with open(htmlfile, 'w', encoding="utf-8") as file:
            file.write(htm.html_top())
    except IOError as err:
        sys.exit(err)
    # Read database
    with con:
        records = con.execute('SELECT * FROM downloads')
        with open(htmlfile, 'a', encoding="utf-8") as file:
            for row in records:
                file.write('  <tr>\n')
                # Weird formatting below is for pretty html.
                file.write(f'''    <td>{row[0]}</td>
    <td>{row[1]}</td>
    <td>{row[2]}</td>
    <td>{row[3]}</td>
''')
                file.write('  </tr>\n')
            file.write(htm.html_bottom())


def init_db(logpath, opt, verbose):
    """Initialise database.

    Similar to main() but reads all logs that start with 'logpath'
    and does NOT check timestamp before counting.

    Parameters
    ----------
    logpath : string
        Path to access logs.
    opt : dict
        Parameters from download_counter.cfg.
    verbose : bool
        Verbose when True.

    Returns
    -------
    None

    """
    if verbose:
        print('\nInitalising\n-----------')
    try:
        conn = sqlite3.connect(opt['dbase'],
                               detect_types=sqlite3.PARSE_DECLTYPES |
                               sqlite3.PARSE_COLNAMES)
        # Initialise table
        conn.execute('DROP TABLE IF EXISTS downloads')
        sql_table(conn)
        for acclog in iglob(logpath + '*', recursive=False):
            if verbose:
                print(f'Using log: "{acclog}"')
            if acclog.endswith('.gz'):
                try:
                    with gzip.open(acclog, 'rt') as file:
                        log_to_sql(conn, file, opt['searchstring'])
                except FileNotFoundError as err:
                    print(err)
            else:
                try:
                    with open(acclog, 'r', encoding="utf-8") as file:
                        log_to_sql(conn, file, opt['searchstring'])
                except FileNotFoundError as err:
                    print(err)
        # HTML output
        if opt['html_out']:
            write_html(conn, opt['html_out'])
    except sqlite3.OperationalError as err:
        sys.exit(err)
    finally:
        conn.commit()
        conn.close()


def main(opt):
    """Count downloads from access logs.

    Search for file names in the access logs that match the search criteria,
    and update the database as necessary. The database is created
    automatically if it does not exist. Downloads with timestamps older than
    the last update are ignored.

    Parameters
    ----------
    opt : dict
       Contains string values: acclogs, dbase, searchstring, and html_out.

    Returns
    -------
    None

    """
    _modified = False
    # Connect to database
    try:
        conn = sqlite3.connect(opt['dbase'],
                               detect_types=sqlite3.PARSE_DECLTYPES |
                               sqlite3.PARSE_COLNAMES)
        # Add table if not exists.
        sql_table(conn)
        # Get timestamp of most recent database entry
        db_last_updated = get_db_time(conn)
        # Get data from access.log(s)
        for log in opt['acclogs']:
            try:
                with open(log, 'r', encoding="utf-8") as file:
                    _modified = log_to_sql(conn, file, opt['searchstring'],
                                           db_last_updated)
            except FileNotFoundError as err:
                # If this accesslog doesn't exist, print error and continue.
                print(err)
        # HTML output
        if opt['html_out']:
            write_html(conn, opt['html_out'])
    except sqlite3.OperationalError as err:
        sys.exit(err)
    finally:
        if _modified:
            conn.commit()
            conn.execute("VACUUM")
        conn.close()


def log_to_sql(con, file, searchstring, timecheck=None):
    """Copy download data from log file to database.

    Read one log file and update database.
    Updating is handled by :func:`~download_counter.update_db`.

    Parameters
    ----------
    con : connection
        Connection to the database.
    file : _io.TextIOWrapper
        Pointer to access log.
    searchstring : string
        Regex pattern for filename in log.
    timecheck : datetime
        Initialise if timecheck=None.

    Returns
    -------
    bool
        True when database has been modified.

    """
    _modified = False
    if not timecheck:
        timecheck = datetime.min
    log = file.readlines()
    for line in log:
        for regex in searchstring:
            data = get_record(line, regex)
            if data:
                if data[1] > timecheck:
                    update_db(con, data[0], data[1])
                    _modified = True
    return _modified


def get_config(cla):
    """Return dict of arguments from download_counter.cfg.

    Config values are retrieved by :func:`~download_counter.list_section`.
    Also print parameters from command line and config file when --verbose
    command line argument is passed.

    Parameters
    ----------
    cla : argparse.Namespace
        Command line switches.

    Returns
    -------
    dict
        Values from configuration file.

    """
    config = configparser.ConfigParser()
    config.read('download_counter.cfg')

    accesslogs = list_section(config, 'ACCESSLOGS')
    sqlite = first_item_in_section(config, 'SQLITE')
    files = list_section(config, 'FILENAMES')
    path = first_item_in_section(config, 'FILEPATH')
    webpage = first_item_in_section(config, 'WEBPAGE')

    re_patterns = [f'GET {re.escape(path)}.*{re.escape(file)}'
                   for file in files]

    if cla.verbose:
        print('\ndownload_counter.cfg arguments:')
        print('-------------------------------')
        print('ACCESSLOGS: \t', accesslogs)
        print('SQLITE: \t', sqlite)
        print('FILENAMES: \t', files)
        print('FILEPATH: \t', path)
        print('WEBPAGE: \t', webpage, '\n')
        for exp in re_patterns:
            print(f'Search for: "{exp}"')

    return {'acclogs': accesslogs, 'dbase': sqlite,
            'searchstring': re_patterns, 'html_out': webpage}


def list_section(cfg, section):
    """Return list of values from cfg section.

    Parameters
    ----------
    cfg : configparser.ConfigParser
        The ConfigParser object.
    section : string
        Section key.

    Returns
    -------
    list
        List of zero or more values.

    """
    try:
        return [cfg[section][key] for key in cfg[section]]
    except KeyError:
        return []


def first_item_in_section(cfg, section):
    """Return the first item from cfg section.

    Parameters
    ----------
    cfg : configparser.ConfigParser
        The ConfigParser object.
    section : string
        Section key.

    Returns
    -------
    string
        First value from section, or empty string.

    """
    try:
        return cfg.items(section)[0][1]
    except (IndexError, configparser.NoSectionError):
        return ""


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                description='Process access log to tally downloads.')
    # Show docs
    parser.add_argument('-d', '--docs', action='store_true',
                        help='show documentation and exit')
    # Initialise
    parser.add_argument('-i', '--init', metavar='path/to/logfiles')
    # Verbose
    parser.add_argument('-v', '--verbose', action='store_true')
    # Show version
    parser.add_argument('-V', '--version', action='version',
                        version='%(prog)s 0.5.0')

    args = parser.parse_args()

    if args.docs:
        print(__doc__)
        sys.exit(0)

    if args.verbose:
        print('\nCommand line arguments:\n-----------------------')
        for arg in vars(args):
            print(f'--{arg}  \t{getattr(args, arg)}')

    options = get_config(args)

    if args.init:
        init_db(args.init, options, args.verbose)
    else:
        main(options)

    if args.verbose:
        print_table(options['dbase'])
