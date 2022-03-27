#############
Customisation
#############

Before use, the **dlcounter.cfg** file must be customised to suit your
server setup. This file must be in the same directory as
**dlcounter.py**.

Below are descriptions of the sections of the config file, and suggested
settings for common setups based on a WordPress installation running on Nginx
and Ubuntu Linux.


[ACCESSLOGS]
============

Specify the log file(s) to analyse.

Typically, for a WordPress site on Nginx, this will be: 
:code:`/var/log/nginx/access.log`, which contains data since the last log
rotation. Provided that downloadcounter runs immediately before log rotation it
is sufficient to analyze just this one log file once per day. See the
:ref:`"Log Rotation" <logrotate>` section for more information about how to
use downloadcounter with logrotate.

Example
-------
.. code-block:: text

   [ACCESSLOGS]
   log1 = /var/log/nginx/access.log


Downloads are only counted if their time stamp is more recent than any
downloads already counted. If it is necessary to analyze aditional (older) log
files, then the files must be listed oldest first. All log files listed here
must be plain text files.

Example
-------
.. code-block:: text

   [ACCESSLOGS]
   log1 = /var/log/nginx/access.log.1
   log2 = /var/log/nginx/access.log


[FILEPATH]
==========

The first part of the search string to identify the downloads in the log files.

This version of Download Counter supports only one FILEPATH parameter.
Typically the downloads to be counted will have a common file path, which
for WordPress sites is in the form:

.. code-block:: text

   .../wp-content/uploads/*<year>*/*<month>*/*<filename>*

As "/wp-content/uploads/" is common to all download files, this is used
as the first part of the search string when finding downloaded files.

Example
-------
.. code-block:: text

   [FILEPATH]
   path = /wp-content/uploads/


[FILENAMES]
===========

The last part of the file(s) to search for in the log files. Typically this
will be a list of file extensions.

Example
-------
.. code-block:: text

   [FILENAMES]  
   file1 = .zip
   file2 = .exe


[WEBPAGE]
=========

The location for html output.

Download Counter generates a web page for viewing the download totals.
Typically this will be located within the public html directory of your
website. **This must be a fully qualified path**. If omitted, no html will
be generated.

Example
-------
.. code-block:: text

   [WEBPAGE]
   path = /var/www/html/downloads.html


[DATETIME]
==========

Datetime formats for reading access logs and writing the html webpage.
This section has two settings, both of which are *required*:

datetime_read
-------------

Format for reading access logs.

Default:
   %d/%b/%Y:%H:%M:%S %z

   The default matches: "01/Jan/2022:23:35:05 +0000"

datetime_write
--------------
Format for writing html webpage.

Default:
   %a %d %b %H:%M

   The default matches: "Mon 01 Jan 18:35"
