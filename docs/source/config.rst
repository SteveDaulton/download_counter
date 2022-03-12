Customisation
#############

Before use, the download_counter.cfg file must be customised to suit your
server setup. This file must be in the same directory as download_counter.py.

Below are descriptions of the five sections of the config file, and suggested
settings for common setups based on a WordPress installation on Nginx, running
on Ubuntu Linux.


ACCESSLOGS
**********

Specify the log files to analyse.

Typically, for a WordPress site on Nginx, these will be:
"/var/log/Nginx/access.log" and "/var/log/Nginx/access.log.1", which will
jointly cover any 24 hour period. The logs must be listed oldest first.

Files listed here must be plain text access.log files.

Example
-------
.. code-block:: text

   [ACCESSLOGS]
   log1 = /var/log/Nginx/access.log.1
   log2 = /var/log/Nginx/access.log


SQLITE
******

Specify the location of the database.

Download Counter stores its data in an SQLite database. Typically this will
be in the same directory as the download_counter.py file and can be defined
with just the name of the file as the relative path.

Example
-------
.. code-block:: text

   [SQLITE]
   path = downloads.db


FILEPATH
********

Specify the first part of the file path to search for in the log files.

This version of Download Counter supports only one FILEPATH parameter.
Typically the downloads to be counted will have a common file path, which
for WordPress sites is in the form:
   
   /wp-content/uploads/*<year>*/*<month>*/*<filename>*

As "/wp-content/uploads/" is common to all download files, this is used
as the first part of the search string when finding downloaded files.

Example
-------
.. code-block:: text

   [FILEPATH]
   path = /wp-content/uploads/


FILENAMES
*********

Specify the last part of the file(s) to search for in the log files.

Typically this will be a list of file extensions.

Example
-------
.. code-block:: text

   [FILENAMES]  
   file1 = .zip
   file2 = .exe


WEBPAGE
*******

Specify the location for html output.

Download Counter can optionally generate a web page for viewing the download
totals. Typically this will be located within the public html directory of
your website. The path may be absolute, or relative to the download_counter.py
working directory.

If omitted, no HTML will be generated.

Example
-------
.. code-block:: text

   [WEBPAGE]
   path = /var/www/html/downloads.html

