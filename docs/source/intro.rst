###############
Getting Started
###############

.. _installation:

************
Installation
************

Before you start
================

To avoid problems, read this page in full before running the app on a live
server.


Dependencies
------------

Download Counter requires Python3. Tested with Python 3.8.10 - slightly
earlier versions may work, but are untested.


Permissions
-----------

dlcounter.py may either be run by passing the command to python:

.. code-block:: console

   $ python3 dlcounter.py <args>

or by making dlcounter.py executable, then run by entering the command
*path/name* and (optional) argments:

.. code-block:: console

   $ sudo chmod +x dlcounter.py
   $ dlcounter.py <args>


Reading server access logs requires root / admin access. Run dlcounter.py as
root / admin. For example, to initialise the database on Linux:

.. code-block:: console

   $ sudo ./dlcounter.py -i /var/log/nginx/access.log -v


Installing
==========

To use Download Counter, place **dlcounter.py**, **dlcounter_html.py** and
**dlcounter.cfg** into a suitable directory *outside* of your website. For
example, they could be placed in a folder in your home directory:

.. code-block:: console

   $ mkdir ~/download_counter
   $ mv dlcounter.py ~/download_counter
   $ mv dlcounter_html.py ~/download_counter
   $ mv dlcounter.cfg ~/download_counter
   $ sudo chmod +x ~/download_counter/dlcounter.py


Alternatively, if Download Counter is obtained as an archive file, simply
extract the entire package to a convenient location outside of you
website. Remember to set file execute permission for dlcounter.py
if required.

Files
-----

   - **dlcounter.py** is the main app.
   - **dlcounter.cfg** contains the configuration settings.
     (This file must be :ref:`customised <configuration>` before use.)
   - **dlcounter_html.py** provides an HTML template for html output.
   - **downloads.db** (created when Download Counter is
     :ref:`initialised <cli_init>`) is the database that stores the data.


.. _configuration:

*************
Configuration
*************

Configuration file
==================

The app has a configuration file :doc:`"dlcounter.cfg" <config>` that may be
edited with any plain text editor. For example, to edit with `nano
<https://www.nano-editor.org/dist/latest/nano.html>`_ :

.. code-block:: console

   $ cd ~/download_counter
   $ nano dlcounter.cfg


Sections
--------

   * [ACCESSLOGS]
      One or more server logs to analyse.
   * [FILEPATH]
      The first part of the name of file(s) to be counted from the access log.
   * [FILENAMES]
      The final part of the name of file(s) to be counted from the access log.
      Typically this will be one or more file extensions.
   * [WEBPAGE]
      The HTML file to display download totals.
      Typically this will be within the website html directory.
   * [DATETIME]
      Datetime formats for reading access logs and writing HTML.

      - datetime_read
         Format for reading access logs.
      - datetime_write
         Format for writing html webpage.


Further details can be found in the :doc:`Customisation <config>` section.


Command Line
============

The following command line switches are provided:

   | **-d, \--docs**
   |     Show built-in documentation and exit.
   |
   | **-h, \--help**
   |     Show short help and exit.
   |
   | **-i, \--init**'path/to/access.logs'*
   |     Initialise database. (See: :ref:`"Initialising"<cli_init>`).
   |
   | **-v, \--verbose**
   |     Verbose output.
   |     Prints arguments, options, and the database contents to stdout.
   |     Along with -D (\--debug) this can be useful to check the
   |     configuration and for debugging.
   |
   | **-D, \--debug**
   |     Prints debug information to stdout.
   |     Along with -v (\--verbose) this can be useful to check the
   |     configuration and for debugging.
   |
   | **-V, \--version**
   |     Show version and exit.



.. _cli_init:

Initialising
============

Download Counter is initialised by running dlcounter.py as root/admin
with the -i (\--init) switch, and the path to to the access logs. It is a
good idea to run this manually from the command line with the -i (\--init),
-D (\--debug), and -v (\--verbose) options. Note that the path must include
the base filename.

All access logs in *'path/to/access.logs'*, (including .gz files),
are read. Matching download files are counted regardless of when they were
downloaded. This option overrides [ACCESSLOGS] in dlcounter.cfg and
should only be used on first run. If the database already exists, the downloads
table will be deleted and recreated.


Example
-------
.. code-block:: text

   python dlcounter.py -i '/var/log/nginx/access.log'

This example will read all logs:

   * /var/log/nginx/access.log
   * /var/log/nginx/access.log.1
   * /var/log/nginx/access.log.2.gz
   * /var/log/nginx/access.log.3.gz
   * ...

It does not attempt to read other logs such as :code:`error.log`.

Running the App
===============

After :ref:`initialising <cli_init>` the database, and setting up
the :ref:`configuration <configuration>` options, dlcounter.py may be run at
any time to update the database and html output. To ensure that all downloads
are caught, dlcounter.py should be run immediately prior to log rotation.
(Alternatively, logs from the current and previous day could be analysed.)

Tip:
----

Run the program with the -v (\--verbose) and -D (\--debug) switches,
and redirect output to a text file to check that it is running as expected.


.. _logrotate:

Log Rotation
============

By default, Ubuntu uses logrotate to rotate logs once per day. Ideally,
download counter should be run immediately before the logs are rotated so
that all records for the previous 24 hours are analyzed.


How it works
------------

This example describes the default setup for Ubuntu / Nginx.

The the script ``/etc/cron.daily/logrotate`` runs daily and executes

.. code-block:: bash

   /usr/sbin/logrotate /etc/logrotate.conf

The **logrotate.conf** file contains the global default settings for logrotate
and *includes* additional configuration files in ``/etc/logrotate.d``.

Among the files in ``/etc/logrotate.d`` is the logrotate configuration for
nginx:

.. code-block:: bash

   /var/log/nginx/*.log {
      daily
      missingok
      rotate 14
      compress
      delaycompress
      notifempty
      create 0640 www-data adm
      sharedscripts
      prerotate
         if [ -d /etc/logrotate.d/httpd-prerotate ]; then \
            run-parts /etc/logrotate.d/httpd-prerotate; \
         fi \
      endscript
      postrotate
         invoke-rc.d nginx rotate >/dev/null 2>&1
      endscript
   }


The line ``compress`` specifies that the log files are compressed, but
``delaycompress`` delays the compression of the most recent log until the
next rotation cycle.

The section between ``prerotate`` and ``endscript`` checks for the existence of
the directory ``/etc/logrotate.d/httpd-prerotate``. If it exists, then
*executable* scripts within that directory are run before the logs are rotated.
Thus a script can be scheduled to run immediately before rotation by placing
it in the folder ``/etc/logrotate.d/httpd-prerotate``.


.. note::

  By default, ``run-parts`` requires that script names must consist entirely of
  ASCII upper- and lower-case letters, ASCII digits, ASCII underscores, and
  ASCII minus-hyphens. In particular, **dots are not allowed**, so file
  extensions must not be used.



Example
-------

If ``/etc/logrotate.d/httpd-prerotate`` does not exist, create it:

.. code-block:: console

   $ sudo mkdir /etc/logrotate.d/httpd-prerotate


Create a bash script to run **dlcounter.py**. Initially we will run with
verbose (-v) and debug (-D) options, and redirect the output to a file to
check that it is running as expected

.. code-block:: console

   $ sudo nano /etc/logrotate.d/httpd-prerotate/dlcounter


Example script:
---------------

.. code-block:: bash

   #!/bin/bash

   output="/home/<username>/dlcount.txt"

   date +"%Y-%m-%d %H:%M:%S.%N %z" > $output
   echo -e "-----------------\n" >> $output
   /home/<username>/dlcounter/dlcounter.py -v -D >> $output

And make the script executable:

.. code-block:: bash

   sudo chmod +x /etc/logrotate.d/httpd-prerotate/dlcounter
