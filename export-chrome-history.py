#!/usr/bin/env python

# export-chrome-history
# 
# A script to convert Google Chrome's history file to the standard HTML-ish
# bookmarks file format.
#
# Copyright (c) 2011, 2017-2018 Benjamin D. Esham. This program is released under the
# ISC license, which you can find in the file LICENSE.md.

from __future__ import print_function
import argparse
from os import environ
from os.path import expanduser, join
from platform import system
from shutil import copy, rmtree
import sqlite3
from sys import argv, stderr
from tempfile import mkdtemp

script_version = "2.0.2"

# html escaping code from http://wiki.python.org/moin/EscapingHtml

html_escape_table = {
	"&": "&amp;",
	'"': "&quot;",
	"'": "&#39;",
	">": "&gt;",
	"<": "&lt;",
	}

output_file_template = """<!DOCTYPE NETSCAPE-Bookmark-file-1>

<meta http-equiv='Content-Type' content='text/html; charset=UTF-8' />
<title>Bookmarks</title>
<h1>Bookmarks</h1>

<dl><p>

<dl><dt><h3>History</h3>

<dl><p>{items}</dl></p>\n</dl>"""

def html_escape(text):
	return ''.join(html_escape_table.get(c,c) for c in text)

def sanitize(string):
	res = ''
	string = html_escape(string)

	for i in range(len(string)):
		if ord(string[i]) > 127:
			res += '&#x{:x};'.format(ord(string[i]))
		else:
			res += string[i]

	return res


# Parse the command-line arguments

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
		description="Convert Google Chrome's history file to the standard HTML-based format.",
		epilog="(c) 2011, 2017-2018 Benjamin D. Esham\nhttps://github.com/bdesham/chrome-export")
parser.add_argument("input_file", nargs="?",
		help="The location of the Chrome history file to read. If this is omitted then the script will look for the file in Chrome's default location.")
parser.add_argument("output_file", type=argparse.FileType('w'),
		help="The location where the HTML bookmarks file will be written.")
parser.add_argument("-v", "--version", action="version",
		version="export-chrome-history {}".format(script_version))

args = parser.parse_args()

# Determine where the input file is

if args.input_file:
	input_filename = args.input_file
else:
	if system() == "Darwin":
		input_filename = expanduser("~/Library/Application Support/Google/Chrome/Default/History")
	elif system() == "Linux":
		input_filename = expanduser("~/.config/google-chrome/Default/History")
	elif system() == "Windows":
		input_filename = environ["LOCALAPPDATA"] + r"\Google\Chrome\User Data\Default\History"
	else:
		print('Your system ("{}") is not recognized. Please specify the input file manually.'.format(system()))
		exit(1)

	try:
		input_file = open(input_filename, 'r')
	except IOError as e:
		if e.errno == 2:
			print("The history file could not be found in its default location ({}). ".format(e.filename) +
					"Please specify the input file manually.")
			exit(1)
	else:
		input_file.close()

# Make a copy of the database, open it, process its contents, and write the
# output file

temp_dir = mkdtemp(prefix='export-chrome-history-')
copied_file = join(temp_dir, 'History')
copy(input_filename, copied_file)

try:
	connection = sqlite3.connect(copied_file)
except sqlite3.OperationalError:
	# This error message is a *little* misleading, since the problem actually
	# occurred when we tried to open copied_file, but chances are that if we got
	# to this point then the problem lies with the file itself (e.g. it isn't a
	# valid SQLite database), not with our ability to read the file.
	print('The file "{}" could not be opened for reading.'.format(input_filename))
	rmtree(temp_dir)
	exit(1)

curs = connection.cursor()

try:
	curs.execute("SELECT url, title FROM urls")
except sqlite3.OperationalError:
	print('There was an error reading data from the file "{}".'.format(args.input_file))
	rmtree(temp_dir)
	exit(1)

items = ""
for row in curs:
	if len(row[1]) > 0:
		items += '<dt><a href="{}">{}</a>\n'.format(sanitize(row[0]), sanitize(row[1]))

connection.close()
rmtree(temp_dir)

args.output_file.write(output_file_template.format(items=items))
args.output_file.close()
