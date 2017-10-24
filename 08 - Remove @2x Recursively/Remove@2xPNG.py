#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Usage:
#   python Remove@2xPNG.py -h
#
# Example:
#   python Remove@2xPNG.py Assets -s @2x.png -v
#

import sys
import argparse
import os


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', metavar='folder', nargs=1, type=str, help='the folder of searching files')
    parser.add_argument('-s', '--suffix', required=True, nargs='+', type=str, help='the suffix of searched files')
    parser.add_argument('-v', '--verbose', action='store_true', help='show verbose information')
    args = parser.parse_args()
    # print args

    folder = args.directory[0]

    if not os.path.isdir(folder):
        print '[Error] ' + folder + ' is not a directory'
        return

    for dir_path, folders, files in os.walk(folder):
        # print dir_path, ' ', folders, ' ', files
        for filename in files:
            for suffix in args.suffix:
                if filename.lower().endswith(suffix):
                    file_path = os.path.join(dir_path, filename)
                    if args.verbose:
                        print 'removing %s' % file_path
                    os.remove(file_path)
    print 'Done! Remove all files suffixed with "%s"' % (', '.join(args.suffix))

if __name__ == '__main__':
    sys.exit(main())