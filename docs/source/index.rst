Download Counter
################

:Version: |release|

Contents
--------

.. toctree::
   :maxdepth: 1

   intro
   config
   api
   html


.. include:: ../../README.rst


How it Works
------------

Nginx logs all access traffic in its 'access.log'. On a daily schedule
the logs are rotated by default (Ubuntu / Nginx):

   * access.log -> access.log.1
   * access.log.1 -> access.log.2.gz
   * ...
   * access.log.13.gz -> access.log.14.gz
   * access.log.14.gz -> deleted.

Each file downloaded from a website on the server has a log entry in the
form:

.. code-block:: text

   Remote-IP - - [local-time-date] "GET /path/to/file.ext protocol"/
   status-code bytes_sent "http-referer" "http-user-agent"

As (by default) the 'access.log' file only contains logs for the current
day, this app should be run once per day (by a root cron job), immediately
before log rotation. See the section :ref:`"Log Rotation" <logrotate>` for
how to do this. (Alternatively, both 'access.log' and 'access.log.1'
could be analyzed at any time of day, though this is much less efficient.)

From the log we need to find:

   #. lines containing the file search string
   #. with status code 200
   #. after the last time it was counted

The results are stored in an SQLite database, and written to an HTML file.
