Getting Started
###############

.. _installation:

Installation
============

Dependencies
------------

Download Counter requires Python3. Tested with Python 3.8.10 - slightly
earlier versions may work, but are untested.


Permissions
-----------

download_counter.py may either be run by passing the command to python:

.. code-block:: console

   $ python3 download_counter.py <args>

or (recommended) by making download_counter.py executable, then run by entering
the command *path/name* and (optional) argments:

.. code-block:: console

   $ sudo chmod +x download_counter.py
   $ download_counter.py <args>


Reading server access logs requires root / admin access. Run
download_counter.py as root / admin. For example, to initialise the database
on Linux:

.. code-block:: console

   $ sudo ./download_counter.py -i /var/log/nginx/access.log -v


Installing
----------

To use Download Counter, place **download_counter.py**,
**download_counter_html.py** and **download_counter.cfg** into a suitable
directory *outside* of your website. For example, they could be placed in a
folder in your home directory:

.. code-block:: console

   $ mkdir ~/download_counter
   $ mv download_counter.py ~/download_counter
   $ mv download_counter_html.py ~/download_counter
   $ mv download_counter.cfg ~/download_counter
   $ sudo chmod +x ~/download_counter/download_counter.py


Alternatively, if Download Counter is obtained as a ZIP or other archive file,
simply extract the entire package to a convenient location outside of you
website. Remember to set file execute permission for download_counter.py
if required.

Files
-----

   - **download_counter.py** is the main app.
   - **download_counter.cfg** contains the configuration settings.
     (This file must be :ref:`customised <configuration>` before use.)
   - **download_counter_html.py** provides an HTML template for html output.
   - **downloads.db** (created when Download Counter is
     :ref:`initialised <cli_init>`) is the database that stores the data.


.. _configuration:

Configuration
=============

The app has a configuration file :doc:`"download_counter.cfg" <config>` that
may be edited with any plain text editor. For example, to edit with `nano
<https://www.nano-editor.org/dist/latest/nano.html>`_ :

.. code-block:: console

   $ cd ~/download_counter
   $ nano download_counter.cfg

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

Download Counter is initialised by running download_counter.py as root/admin
with the -i (\--init) switch, and the path to to the access logs. It is a
good idea to run this manually from the command line with the -i (\--init)
and -v (\--verbose) options. Note that the path must include the base filename.
If the path includes spaces, ensure that it is quoted.

All access logs in *'path/to/access.logs'*, (including .gz files),
are read. Matching download files are counted regardless of when they were
downloaded. This option overrides [ACCESSLOGS] in download_counter.cfg and
is only be used on first run.

Example
-------
.. code-block:: text

   python download_counter.py -i '/var/log/nginx/access.log'

This example will read all logs::

      * /var/log/nginx/access.log
      * /var/log/nginx/access.log.1
      * /var/log/nginx/access.log.2.gz
      * /var/log/nginx/access.log.3.gz
      * ...

It does not attempt to read other logs such as :code:`error.log`.

Running the App
===============

After :ref:`initialising <cli_init>` the database, and setting up
the :ref:`configuration <configuration>` options, download_counter.py may
be run at any time to update the database and html output. To ensure that
all downloads are caught, logs from the current and previous day should be
analysed each day.

Tip:
----

Run the program with the -v (\--verbose) and -D (\--debug) switches,
and redirect output to a text file to check that it is running as expected.


Example
-------
.. code-block:: text

   python download_counter.py -v -D > testcron.txt 2>&1

For automatic updating of the download count, schedule a cron job to run
download_counter.py once per day. Ensure that the :doc:`config <config>`
file has been appropriately customised before running.

Creating a cron schedule as root will allow the access.log files to be read.

Example cron jobs
-----------------

To run download_counter.py every minute, with verbose and debug output
printed to a file:

.. code-block:: console

   * * * * * /home/<username>/download_counter/download_counter.py -v -D > /home/<username>/testcron.txt 2>&1

To run download_counter.py quietly once per day at 3:00 am:

.. code-block:: console

   00 03 * * * /home/<username>/download_counter/download_counter.py
