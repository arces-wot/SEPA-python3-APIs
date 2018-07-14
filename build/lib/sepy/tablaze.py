#!/usr/bin python3
# -*- coding: utf-8 -*-
#
#  tablaze.py
#  
#  Copyright 2018 Francesco Antoniazzi <francesco.antoniazzi@unibo.it>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#    _        _     _               
#   | |_ __ _| |__ | | __ _ _______ 
#   | __/ _` | '_ \| |/ _` |_  / _ \
#   | || (_| | |_) | | (_| |/ /  __/
#    \__\__,_|_.__/|_|\__,_/___\___|
#

import prettytable
import json
import re

def tablify(input_json,prefix_file=None):
    """
    This is the method to call when you import tablaze and
    don't use it as a stand alone script.
    input_json can be given as
        - path to json file to be rendere
        - string with the json itself
    prefix_file is not compulsory, and you can give it as
        - path to file containing prefix strings from sparql
        - list of prefix strings
    """
    main({"prefixes": prefix_file, "file": input_json})

def main(args):
    # builds prefix dictionary
    prefixes = {}
    if args["prefixes"] is not None:
        try:
            # this is when args["prefixes"] is a path to file
            with open(args["prefixes"],"r") as prefix_file:
                lines = prefix_file.readlines()
        except:
            # this is when it's a list of strings
            lines = args["prefixes"]
        for line in lines:
            # here we parse the prefixes
            m = re.match(r"prefix ([a-zA-Z]+): <(.+)>",line)
            prefixes[m.groups()[0]] = m.groups()[1]
    
    # loads the json from a file, or tries from the command line argument
    try:
        with open(args["file"],"r") as bz_output:
            json_output = json.load(bz_output)
    except:
        json_output = json.loads(json.dumps(args["file"]))
    
    # setup the table which will be given in output
    variables = json_output["head"]["vars"]
    pretty = prettytable.PrettyTable(variables)
    
    # fills up the table: one line per binding
    for binding in json_output["results"]["bindings"]:
        tableLine = []
        for v in variables:
            if v in binding:
                nice_value = binding[v]["value"]
                if binding[v]["type"]!="literal":
                    for key in prefixes.keys():
                        # prefix substitution
                        nice_value = nice_value.replace(prefixes[key],key+":")
                if nice_value != "":
                    tableLine.append("({}) {}".format(binding[v]["type"],nice_value))
                else:
                    tableLine.append("")
            else:
                # special case: absent binding
                tableLine.append("")
        pretty.add_row(tableLine)
    print(str(pretty))
    print("\n{} result(s)".format(len(json_output["results"]["bindings"])))
    return 0

if __name__ == '__main__':
    import sys
    import argparse
    parser = argparse.ArgumentParser(description="Blazegraph query output formatter into nice tables")
    parser.add_argument("file", help="Output in json format to be reformatted: can be a path or the full json or 'stdin'")
    parser.add_argument("-prefixes", default="./prefixes.txt", help="Optional file containing prefixes to be replaced into the table")
    args = vars(parser.parse_args())
    sys.exit(main(args))
