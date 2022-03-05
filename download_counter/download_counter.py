"""Download counter for nginx.

Reads access.log and looks for files with specified file extensions, which are
then logged in the download stats database (SQLite).


Usage
=====

    Options may either be set via command line switches, or from a
    configuration file.

    Using a config file
    -------------------

    The configuration file ('download_counter.cfg'), if used, must be in the
    same directory as 'download_counter.py'. When the app is run without
    any additional arguments, the app obtains its settings from the config
    file.

    Command line switches
    ---------------------

    Command line switches override any options provided by the config file.

    usage: download_counter.py [-h] [-a] [-f] [-p] [-s ] [-w] [-v] [-d]

Arguments:

    -h,--help: optional
        Show short help and exit.

    -a, --accesslogs: string
        Path to nginx 'access.log'

    -f --files: list, default=[]
        One or more file names or file extensions to count.
        Must be a space separated list if more than one item.
        If not specified, the database will be printed.

        Example:
        Count requests for 'robots.txt', '.jpg' and '.gif' files:

            $ python3 download-counter -f robots.txt .jpg .gif

    -p, --filepath, default=''
        Path download directory. If not supplied, all file names matching
        the -f option(s) will be counted.

        The path may just be the root of the download path, for example,
        if download files are in:

            * .../website/downloads/2001/
            * .../website/downloads/2002/
            * .../website/downloads/.../

        then to catch files in all of these folders:
            $ python3 download-counter -p '/website/downloads/'

    -s, --sqlite: string, optional, default='downloads.db'
        Path to sqlite database

    -w, --webpage: string, optional, default=None
        output path for HTML, disabled if not specified (default: '')

    -v, --version: optional
        show programversion and exit

    -V, --verbose: optional
        print commands and database contents to standard output.

    -d, --docs: optional
        show this documentation and exit


Background
==========

    While there are several WordPress modules for managing downloads, in 2022
    it seems that they are all large, complex modules aimed at e-commerce.
    From a security perspective, it's advisable to avoid presenting a larger
    attack target than absolutely necessary, hence this small download counter
    for NGINX.


How it Works
------------

    NGINX logs all access trafic in its 'access.log'. On a daily schedule
    the logs are rotated by default (Ubuntu):

        * access.log -> access.log.1
        * access.log.1 -> access.log.2.gz
        * ...
        * access.log.13.gz -> access.log.14.gz
        * access.log.14.gz -> deleted.

    Each file downloadled from a website on the server has a log entry in the
    form:

        Remote-IP - - [local-time-date] "GET /path/to/file.ext protocol"
        status-code bytes_sent "http-referer" "http-user-agent"

    As (by default) the 'access.log' file only contains logs for the current
    day, this app should be run once per day (by a root cron job), and check
    both 'access.log' and 'access.log.1' to ensure all relevant requests are
    found.

    From the log we need to find:

        1. lines containing the file name or file extensions
        2. with status code 200
        3. after the last time it was counted

    The results are stored in an SQLite database, and optionally used to
    create an HTML page.

Note:
-----

    --path and --file options are just strings that will be searched for in
    the accesslog file(s). Regex is used to search the log file(s) for:
    "<path-string> any-characters <file-string>"

"""


import sys
import sqlite3
import argparse
import re
from datetime import datetime
from configparser import ConfigParser

import download_counter_html as htm


def default_date_time_format():
    """Return the date-time format of access.log"""
    return '%d/%b/%Y:%H:%M:%S %z'


def print_table(dbase):
    """Print contents of downloads in 'dbase'.
    Used with verbose option.
    """
    sql_get_table = 'SELECT * FROM downloads'
    print('ID \tFile \t\t Timestamp \t\t Total')
    try:
        conn = sqlite3.connect(dbase)
        with conn:
            records = conn.execute(sql_get_table)
            for row in records:
                for val in row:
                    print(val, end ='\t')
                print('')
    except sqlite3.OperationalError as err:
        sys.exit(err)
    conn.close()


def get_db_time(con):
    """Return most recent timestamp from database."""
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    try:
        cur.execute('select timestamp from downloads')
    except sqlite3.OperationalError as err:
        print(err)
    recent = datetime(1, 1, 1)
    for row in cur:
        if row['timestamp'] > recent:
            recent = row['timestamp']
    return recent


def sql_table(con):
    """ Create table if it doesn't exist."""
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
    """
    # pattern = f'GET {re.escape(start)}.*{re.escape(end)}'
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
    """Return timestamp (date-time object) or quit."""
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
    """If fname exists in database, update its download total and timestamp,
    else insert it into the database with a count of 1.
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
    """Write sql data to web page"""
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


def main(acclogs, dbase, searchstring, html_out):
    """Search for file names in the access logs that match
    the search criteria, and update the database.
    """
    _modified = False
    # Connect to database
    try:
        conn = sqlite3.connect(dbase,
                               detect_types=sqlite3.PARSE_DECLTYPES |
                               sqlite3.PARSE_COLNAMES)
        # Add table if not exists.
        sql_table(conn)
        # Get timestamp of most recent database entry
        db_last_updated = get_db_time(conn)
        # Get data from access.log(s)
        for log in acclogs:
            try:
                with open(log, 'r', encoding="utf-8") as file:
                    for regex in searchstring:
                        log = file.readlines()
                        for line in log:
                            data = get_record(line, regex)
                            if data:
                                if data[1] > db_last_updated:
                                    update_db(conn, data[0], data[1])
                                    _modified = True
            except FileNotFoundError as err:
                # If this accesslog doesn't exist,
                # print error and continue.
                print(err)
        # HTML output
        if html_out:
            write_html(conn, html_out)
    except sqlite3.OperationalError as err:
        sys.exit(err)
    finally:
        if _modified:
            conn.commit()
            conn.execute("VACUUM")
        conn.close()


def get_args(accesslogs, sqlite, files, path, webpage, verbose):
    """Return dict of arguments from command line and / or
    from download_counter.cfg
    Command line arguments take priority.
    """
    config = ConfigParser()
    rslt = config.read('download_counter.cfg')

    cfg_accesslogs = list_section(config, 'ACCESSLOGS')
    cfg_sqlite = first_item_in_section(config, 'SQLITE')
    cfg_files = list_section(config, 'FILENAMES')
    cfg_path = first_item_in_section(config, 'FILEPATH')
    cfg_webpage = first_item_in_section(config, 'WEBPAGE')

    if verbose:
        print('\ndownload_counter.cfg arguments:')
        print('-------------------------------')
        print('ACCESSLOGS: \t', cfg_accesslogs)
        print('SQLITE: \t', cfg_sqlite)
        print('FILENAMES: \t', cfg_files)
        print('FILEPATH: \t', cfg_path)
        print('WEBPAGE: \t', cfg_webpage)

    if not accesslogs:
        accesslogs = cfg_accesslogs
    if not sqlite:
        sqlite = cfg_sqlite
    if not files:
        files = cfg_files
    if not path:
        path = cfg_path
    if not webpage:
        webpage = cfg_webpage
    re_patterns = [f'GET {re.escape(path)}.*{re.escape(file)}'
                   for file in files]
    return {'acclogs' : accesslogs, 'dbase' : sqlite,
            'searchstring' : re_patterns, 'html_out' : webpage}
    

def list_section(cfg, section):
    """Return list of values from cfg section.
    """
    return [cfg[section][key] for key in cfg[section]]


def first_item_in_section(cfg, section):
    """Return the first item from cfg section.
    """
    return cfg[section][[key for key in cfg[section]][0]]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                description='Process access log to tally downloads.')
    # Access log location
    parser.add_argument('-a', '--accesslogs', nargs="+",
                        type=str, metavar='log',
                        default=[],
                        help='list [paths to "access.log"] file(s)')
    # Database location
    parser.add_argument('-s', '--sqlite', type=str, metavar='path/to/dbase',
                        help='output SQLite database file')
    # Files to count
    parser.add_argument('-f', '--files', action="extend", nargs="+",
                        type=str, metavar='fname',
                        default=[],
                        help='list [filename/extension(s)] to monitor')
    parser.add_argument('-p', '--filepath',
                        type=str, metavar='fpath',
                        help='path to download files')
    # Webpage output
    parser.add_argument('-w', '--webpage', type=str, metavar='path/to/.html',
                        help='output path for HTML')
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s 0.1.0')
    parser.add_argument('-V', '--verbose', action='store_true',
                        help='show documentation and exit')
    parser.add_argument('-d', '--docs', action='store_true',
                        help='show documentation and exit')

    args = parser.parse_args()

    if args.docs:
        print(__doc__)
        sys.exit(0)

    if args.verbose:
        print('\nCommand line arguments:\n-----------------------')
        for arg in vars(args):
            print(f'--{arg}  \t{getattr(args, arg)}')
    opt = get_args(args.accesslogs, args.sqlite, args.files,
                   args.filepath, args.webpage, args.verbose)
    if args.verbose:
        print('\nDatabase downloads table:\n-------------------------')
        print_table(opt['dbase'])
    main(opt['acclogs'], opt['dbase'], opt['searchstring'], opt['html_out'])
