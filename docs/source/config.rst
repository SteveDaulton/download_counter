Customisation
#############

Before use, the **download_counter.cfg** file must be customised to suit your
server setup. This file must be in the same directory as
**download_counter.py**.

Below are descriptions of the sections of the config file, and suggested
settings for common setups based on a WordPress installation running on Nginx
and Ubuntu Linux.


[ACCESSLOGS]
************

Specify the log files to analyse.

Typically, for a WordPress site on Nginx, these will be:
:code:`/var/log/nginx/access.log` and :code:`/var/log/nginx/access.log.1`,
which will jointly cover any 24 hour period. **The logs must be listed oldest
first**. Files listed here must be plain text access.log files.

Example
-------
.. code-block:: text

   [ACCESSLOGS]
   log1 = /var/log/nginx/access.log.1
   log2 = /var/log/nginx/access.log


[FILEPATH]
**********

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
***********

The last part of the file(s) to search for in the log files.

Typically this will be a list of file extensions.

Example
-------
.. code-block:: text

   [FILENAMES]  
   file1 = .zip
   file2 = .exe


[WEBPAGE]
*********

The location for html output.

Download Counter generates a web page for viewing the download totals.
Typically this will be located within the public html directory of your
website. **This must be a fully qualified path**. If omitted, no HTML will
be generated.

Example
-------
.. code-block:: text

   [WEBPAGE]
   path = /var/www/html/downloads.html


[DATETIME]
**********

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
