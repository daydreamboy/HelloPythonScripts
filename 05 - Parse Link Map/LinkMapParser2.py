#!/usr/bin/env python
# -*- coding: utf-8 -*-

# History:
#   2017-02-17 wesley_chen <TODO>
#
# Usage:
#   1. LinkMapParse.py (find Link Map file on current dir. Output result on current dir)
#   2. LinkMapParser.py <path/to/link map file> (Output result on current dir)
#   3. LinkMapParser.py <path/to/link map file> <path/to/result file>

import sys
import os
import logging
import json
import codecs
from collections import OrderedDict
import argparse
import textwrap

# script info
script_version = 1.0
script_author = 'wesley_chen'
script_email = 'wesley4chen@gmail.com'


# extract middle part of string excluding `start` and `end` string
def extract_string(string, start, end):
    return string[string.index(start) + len(start) : string.index(end)]


# http://stackoverflow.com/questions/2553354/how-to-get-a-variable-name-as-a-string-in-python
def dump_object(obj):
    for k, v in list(locals().iteritems()):
        if v is obj:
            obj_name = k
            break
    print(str(obj_name) + ": %s" % obj)


def dict_to_json_file(dict_object, file_path):
    ordered_dict = OrderedDict(sorted(dict_object.items(), key=lambda t: t[0]))
    # logging.warning("pod_source_dict is: %s" % pod_source_dict)
    # logging.warning("json is: %s" % json.dumps(pod_source_dict))
    out_file = open(file_path, "w")
    out_file.writelines(json.dumps(ordered_dict))
    out_file.close()

suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']

# http://stackoverflow.com/questions/14996453/python-libraries-to-calculate-human-readable-filesize-from-bytes
def humansize(nbytes):
    if nbytes == 0: return '0 B'
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])


class LibraryModel:
    def __init__(self, name):
        self.name = name
        self.size = None
        self.members = []

    def __str__(self):
        return self.name + ', ' + str(self.size) + ', ' + str(self.members)

    # def __repr__(self):
    #     return self.name + str(self.size) + str(self.members)


class ObjectModel:
    def __init__(self, name, tag):
        self.name = name
        self.tag = tag
        self.size = None
        self.members = []


class SymbolModel:
    def __init__(self, name, tag, size):
        self.name = name
        self.tag = tag
        self.size = size


def main():

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=textwrap.dedent('''
    -----------------------------------------
       A script for parsing link map file
    -----------------------------------------

    '''),
                                     epilog='''
    Report bug to <{script_email}>. (Version: {script_version})
    '''.format(**globals()))

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

    parser.add_argument('--version', action='version', version='%(prog)s {script_version}'.format(**globals()))
    parser.add_argument('-v', '--verbose', action='store_true', help='show verbose information')

    args = parser.parse_args()

    print("Argument values: %s" % args)

    current_dir = os.getcwd()
    output_dict = {}
    library_dict = {}

    source_file_path = args.linkmap_path
    target_file_path = os.getcwd()
    if args.file is not None:
        target_file_path = args.file

    # http://stackoverflow.com/questions/1592925/decoding-mac-os-text-in-python
    with codecs.open(source_file_path, 'r', 'mac-roman') as f:
        file_content = f.read()
        f.close()
    # Get `arch` part
    arch_part = extract_string(file_content, "# Arch:", "# Object files:")
    output_dict["Arch"] = arch_part.strip()

    # Get `object file` part
    object_files_part = extract_string(file_content, "# Object files:\n", "\n# Sections:")
    object_files_list = object_files_part.splitlines()
    object_files_list = filter(None, object_files_list)  # remove all empty items if it's an empty string
    object_files_dict = {}    # key: int(oid), value: file_name.o
    object_library_dict = {}  # key: xxx.a, value: [yyy.o, zzz.o, ....]
    dump_object(object_files_list)
    for line in object_files_list:
        part_list = line.split("]")
        file_id = part_list[0].strip("[ ")
        file_name = os.path.basename(part_list[1]).strip()

        if file_name.find("(") != -1:
            object_file_name = file_name.split("(")[1].strip(")")
            object_files_dict[int(file_id)] = object_file_name

            library_name = file_name.split("(")[0]
            if not library_name.endswith(".a"):
                library_name += ".framework"

            if library_name not in library_dict:
                library_dict[library_name] = LibraryModel(library_name)

            library_model = library_dict[library_name]
            library_model.members.append(ObjectModel(object_file_name, file_id))
        else:
            object_files_dict[int(file_id)] = file_name

            if file_name.endswith(".o"):
                if "main project" not in library_dict:
                    library_dict['main project'] = LibraryModel('main project')

                library_model = library_dict['main project']
                library_model.members.append(ObjectModel(file_name, file_id))

                dump_object(library_model)
            else:
                library_dict[file_name] = LibraryModel(file_name)

    # dump_object(library_dict)
    # dump_object(object_files_dict)
    return

    dict_to_json_file(object_files_dict, os.path.join(current_dir, 'object_files_dict.json'))
    dict_to_json_file(object_library_dict, os.path.join(current_dir, 'object_library_dict.json'))

    # Get `Symbols` part
    symbol_part = extract_string(file_content, "# Address	Size    	File  Name\n", "\n\n# Dead Stripped Symbols:")
    symbol_list = symbol_part.splitlines()
    symbol_list = filter(None, symbol_list)  # remove all empty items if it's an empty string
    symbol_object_dict = {}
    for line in symbol_list:
        part_list = line.split("\t")
        if len(part_list) != 3:
            continue  # ignore \n line
        symbol_size = part_list[1].strip()

        subpart_list = part_list[2].split("] ")
        symbol_object_id = int(subpart_list[0].strip("[ "))
        symbol_name = subpart_list[1]

        object_file_name = object_files_dict[symbol_object_id]

        if object_file_name in symbol_object_dict:
            temp_dict = symbol_object_dict[object_file_name]
            if symbol_name in temp_dict:
                temp_size = int(temp_dict[symbol_name])
                temp_size += int(symbol_size, 0)
                temp_dict[symbol_name] = temp_size
            else:
                temp_dict[symbol_name] = int(symbol_size, 0)
            symbol_object_dict[object_file_name] = temp_dict
        else:
            symbol_object_dict[object_file_name] = {symbol_name: int(symbol_size, 0)}

        if object_file_name + ".size" in symbol_object_dict:
            temp_int = symbol_object_dict[object_file_name + ".size"]
            temp_int += int(symbol_size, 0)
            symbol_object_dict[object_file_name + ".size"] = temp_int
        else:
            symbol_object_dict[object_file_name + ".size"] = int(symbol_size, 0)

        # dump_object(symbol_size)
        # dump_object(symbol_object_id)
        # dump_object(symbol_name)
    # dump_object(symbol_object_dict)
    dict_to_json_file(symbol_object_dict, os.path.join(current_dir, 'symbol_object_dict.json'))

    module_dict = {}
    for library_name in object_library_dict:
        object_list = object_library_dict[library_name]

        if len(object_list) != 0:
            library_size = 0
            temp_dict = {}
            for object_file_name in object_list:
                if object_file_name in symbol_object_dict:
                    object_size = symbol_object_dict[object_file_name + ".size"]
                    library_size += object_size
                    temp_dict[object_file_name] = symbol_object_dict[object_file_name]
                    temp_dict[object_file_name + ".size"] = symbol_object_dict[object_file_name + ".size"]
                else:
                    logging.warning("%s not found in symbol_object_dict" % object_file_name)
            module_dict[library_name] = temp_dict
        else:
            if library_name in symbol_object_dict:
                library_size = symbol_object_dict[library_name + ".size"]
                module_dict[library_name] = symbol_object_dict[library_name]
            else:
                logging.warning("%s not found in symbol_object_dict" % library_name)
        dump_object("%s size: %s" % (library_name, humansize(library_size)))
        module_dict[library_name + ".size"] = int(library_size)

    output_dict["Module"] = module_dict

    # logging.warning("output_dict: %s" % output_dict)
    # dict_to_json_file(output_dict, os.path.join(current_dir, 'size_info.json'))

if __name__ == '__main__':
    sys.exit(main())
