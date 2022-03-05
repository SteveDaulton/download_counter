"""HTML code for generating web page output.

download_counter.py creates table data between html_top()
and html_bottom().

This file may be modified according to need.
"""


def html_top():
    """Return beginning of html page."""
    return """<!DOCTYPE html>
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
    """Return end of html page."""
    return """</table>
</body>
</html>"""
