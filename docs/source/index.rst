Download Counter
================

Contents
--------

.. toctree::
   :maxdepth: 1

   intro
   config
   api
   html

**Download Counter** is stand-alone Python app to keep a tally of downloads from
a website.

This app was developed for use with WordPress / Nginx / Ubuntu, but will
probably work on other platforms with minimal alterations. Patches to support
other common platforms are welcome.

The app is easily :ref:`installed <installation>`, and may be :ref:`configured
<configuration>` to suit the server setup.


Rationale
---------

While there are several WordPress modules for managing downloads, in 2022
it seems that they are all large, complex modules aimed at e-commerce.
From a security perspective, it's advisable to avoid presenting a larger
attack target than absolutely necessary, hence this small download counter.


What it does:
-------------

This app scans the server access logs and searches for downloaded files that
match the given search criteria. When found, they are logged in an SQLite
database, along with the download timestamp and a count of how many times
the file has been downloaded.

The app may optionally generate an HTML page to display the database contents.


How it Works
------------

Nginx logs all access traffic in its 'access.log'. On a daily schedule
the logs are rotated by default (Ubuntu):

   * access.log -> access.log.1
   * access.log.1 -> access.log.2.gz
   * ...
   * access.log.13.gz -> access.log.14.gz
   * access.log.14.gz -> deleted.

Each file downloaded from a website on the server has a log entry in the
form:

   Remote-IP - - [local-time-date] "GET /path/to/file.ext protocol"
   status-code bytes_sent "http-referer" "http-user-agent"

As (by default) the 'access.log' file only contains logs for the current
day, this app should be run once per day (by a root cron job), and check
both 'access.log' and 'access.log.1' to ensure all relevant requests are
found.

From the log we need to find:

   #. lines containing the file name or file extensions
   #. with status code 200
   #. after the last time it was counted

The results are stored in an SQLite database, and optionally used to
create an HTML page.
