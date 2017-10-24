#!/usr/bin/env python
# -*- coding: utf-8 -*-

# History:
#   2017-02-21 wesley_chen <TODO>
#
# Usage:
#   1. LinkMapParse.py (find Link Map file on current dir. Output result on current dir)
#   2. LinkMapParser.py <path/to/link map file> (Output result on current dir)
#   3. LinkMapParser.py <path/to/link map file> <path/to/result file>
"""
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('integers', metavar='b', type=int, nargs='+',
                    help='an integer for the accumulator')
parser.add_argument('--sum', dest='accumulate', action='store_const',
                    const=sum, default=max,
                    help='sum the integers (default: find the max)')

args = parser.parse_args()
print args.accumulate(args.integers)
"""

import argparse
import textwrap

# Instantiate the parser
parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description=textwrap.dedent('''
-----------------------------------------
   A script for parsing link map file
-----------------------------------------

'''),
                                 epilog='''
Report bug to <wesley4chen@gmail.com>
''')

# Required positional argument
parser.add_argument("linkmap_path", metavar="path", type=str,
                    help='the path of LinkMap file')

# Optional positional argument
parser.add_argument('-l', '--level', type=int, nargs=1, choices=range(1, 4), default=2,
                    help='''
                    the detail level of parsing (default: %(default)s).
                     1: .a files, 2: .o files, 3: symbols''')

parser.add_argument('-f', '--file', type=str, nargs=1,
                    help='output to the file at the path')

parser.add_argument('-r', dest="readable_size", action='store_true',
                    help='show readable size')

parser.add_argument('--version', action='version', version='%(prog)s 2.0')
parser.add_argument('-v', '--verbose', action='store_true', help='show verbose information')

args = parser.parse_args()

print("Argument values: %s" % args)
# print("pos_arg : " + str(args.pos_arg))
# print("opt_pos_arg : " + str(args.opt_pos_arg))
# print("opt_arg : " + str(args.opt_arg))
# print("switch : " + str(args.switch))
