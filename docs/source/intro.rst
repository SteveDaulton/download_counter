Getting Started
###############

.. _installation:

Installation
============

To use Download Counter, place **download_counter.py**,
**download_counter_html.py** and **download_counter.cfg** in a suitable
location *outside* of your website. For example, they could be placed in a
folder in your home directory:

.. code-block:: console

   $ mkdir ~/download_counter
   $ cp download_counter.py ~/download_counter
   $ cp download_counter_html.py ~/download_counter
   $ cp download_counter.cfg ~/download_counter


Alternatively, if Download Counter is obtained as a ZIP or other archive file,
simply extract the entire package to a convenient location outside of you
website.

**download_counter.py** is the main app.

**download_counter.cfg** contains the configuration settings that are *required*
by download_counter.py.

**download_counter_html.py** provides an HTML template that is required for
html output (optional, enabled by default).


.. _configuration:

Configuration
=============

The app has a configuration file **"download_counter.cfg"** that may be easily
edited with any plain text editor. For example, to edit with `nano
<https://www.nano-editor.org/dist/latest/nano.html>`_ :

.. code-block:: console

   $ cd ~/download_counter
   $ nano download_counter.cfg

The configuration file has five sections:

   * ACCESSLOGS
      One or more server logs to analyse.
   * SQLITE
      The database file that will store the results.
   * FILEPATH
      The first part of the name of file(s) to be counted from the access log.
   * FILENAMES
      The final part of the name of file(s) to be counted from the access log.
      Typically this will be one or more file extensions.
   * WEBPAGE
      The HTML file to display download totals.
      Typically this will be within the website html directory.


Further details can be found in the :doc:`Customisation <config>` section.


Command Line
============

The following command line switches are provided:

* **-d, -\-docs**
   Show built-in documentation and exit.
* **-h, -\-help**
   Show short help and exit.

.. _cli_init:

* **-i, -\-init** *'path/to/access.logs'*
   Initialise database.

   This option is required if you wish to count downloads in old
   archived '.gz' files. The path to the base access.log file must be
   provided. If the path includes spaces, ensure that it is quoted.

   All access logs in path, (including .gz files), are read.
   Matching download files are counted regardless of when they were
   downloaded, so this option should only be used on first run, (before
   the database contains data). This option overrides ACCESSLOGS in
   download_counter.cfg.

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

* **-v, -\-verbose**
   Verbose output.

   When run with this option, commands and database contents are printed.
   This can be useful to check that the configuration is set up correctly.

* **-V, -\-version**
   Show program version and exit.



Running the App
===============

On first run you will probably want to run download_counter.py manually
from the command line with the -i (-\-init) and -v (-\-verbose) options.
This will allow Download Counter to analyse old ".gz" archived logs in
addition to the plain text logs. See :ref:`Initialise database <cli_init>`
option above.

For automatic updating of the download count, schedule a cron job to run
download_counter.py once per day. Ensure that the :doc:`config <config>`
file has been appropriately customised before running.

To ensure that everything is running as expected, it may be useful to
initially run the program with the -v (-\-verbose) switch and redirect
standard out to a text file for inspection.

Example
-------
.. code-block:: text

   python download_counter.py -v > test.txt
