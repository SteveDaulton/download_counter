Download Counter
================

A standalone Python app to keep a tally of downloads from a website.

This app was developed for use with WordPress / NGINX / Ubuntu, but will
probably work on other platforms with minimal alterations. Patches to support
other common platforms are welcome.


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
