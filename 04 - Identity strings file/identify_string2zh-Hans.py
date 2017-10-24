#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Usage:
#   python identify_string2zh-Hans.py
#

import sys
import os
import logging


def main():
    current_dir = os.getcwd()
    source_file_name = "Localizable.strings"
    source_file_path = os.path.join(current_dir, source_file_name)
    target_file_path = os.path.join(current_dir, *["zh-Hans.lproj", source_file_name])

    source_file_content = ""
    target_file_content = ""
    with open(source_file_path) as f:
        source_file_content = f.readlines()

    if len(source_file_content) == 0:
        logging.warning("%s is empty!" % source_file_name)
        exit(1)

    for line in source_file_content:
        if line.find("=") == -1:
            target_file_content += line
        else:
            parts = line.split("=")
            new_line = parts[0] + "=" + parts[0] + ";\n"
            target_file_content += new_line

    logging.warning("%s" % target_file_content)

    basedir = os.path.dirname(target_file_path)
    if not os.path.exists(basedir):
        os.makedirs(basedir)

    out_file = open(target_file_path, "w")
    out_file.write(target_file_content)
    out_file.close()

if __name__ == '__main__':
    sys.exit(main())

