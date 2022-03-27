# -*- coding: utf-8 -*-
"""HTML code for generating web page output.

dlcounter.py creates table data between ``html_top()``
and ``html_bottom()``. This module provides the rest of the HTML for the
download counter web page.


This file may be modified according to need.

"""


def html_top(timestamp):
    """Return beginning of html page.

    Returns
    -------
    string
        HTML output.

    """
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<style>
table, th, td {
 border: 1px solid black;
 border-collapse: collapse;
}
th {
 background-color: #96D4D4;
}
td {
 text-align: center;
}
</style>
<title>Download counter</title>
</head>
<body>
<h1>Downloads</h1>
<h2>Updated {timestamp}</h2>

<!-- You probably don't want to edit below this line -->

<table style="width:80%">
  <tr>
    <th>ID</th>
    <th>File</th>
    <th>Date</th>
    <th>Downloads</th>
  </tr>
"""


def html_bottom():
    """Return end of html page.

    Returns
    -------
    string
        HTML output.

    """
    return """</table>
</body>
</html>"""
