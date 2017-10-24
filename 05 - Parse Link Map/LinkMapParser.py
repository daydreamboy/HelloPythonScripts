#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Usage:
#   LinkMapParser.py -h
#
# Example:
#   python LinkMapParser.py ./HelloLinkMap-LinkMap-normal-arm64.txt --json -l3 -s size --descend
#   python LinkMapParser.py ./ONEPassportSDK_Example-LinkMap-normal-x86_64.txt -rv -l2 -s size --library libONEPassportSDK.a --descend

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
    return string[string.index(start) + len(start): string.index(end)]


def dump_object(obj):
    # http://stackoverflow.com/questions/2553354/how-to-get-a-variable-name-as-a-string-in-python
    for k, v in list(locals().iteritems()):
        if v is obj:
            obj_name = k
            break
    print(str(obj_name) + ": %s" % obj)


def dict_to_json_file(dict_object, file_path):
    ordered_dict = OrderedDict(sorted(dict_object.items(), key=lambda t: t[0]))
    out_file = open(file_path, "w")
    out_file.writelines(json.dumps(ordered_dict))
    out_file.close()


def humansize(nbytes):
    # http://stackoverflow.com/questions/14996453/python-libraries-to-calculate-human-readable-filesize-from-bytes
    suffixes = ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB']

    if nbytes == 0: return '0 B'
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])


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
    parser.add_argument('-l', '--level', type=int, nargs=1, choices=range(1, 4), default=[2],
                        help='''
                        the detail level of parsing (default: %(default)s).
                         [1] .a files, [2] .o files, [3] symbols''')

    parser.add_argument('-j', '--json', action='store_true',
                        help='output by json format')

    parser.add_argument('-s', '--sorted', dest="sorted", choices=['name', 'size'], default='name',
                        help='ordered by name or size')

    parser.add_argument('--descend', dest="descend", action='store_true',
                        help='ascend or descend order')

    parser.add_argument('--library', dest="library", nargs='+',
                        help='filter some libraries. If not specified, all libraries are shown.')

    parser.add_argument('--object', dest="object", nargs='+',
                        help='filter some object. If not specified, all objects are shown.')

    parser.add_argument('-r', dest="readable_size", action='store_true',
                        help='show readable size')

    parser.add_argument('--debug', dest="debug", action='store_true', help='dump intermediate json files for debugging')
    parser.add_argument('--version', action='version', version='%(prog)s {script_version}'.format(**globals()))
    parser.add_argument('-v', '--verbose', action='store_true', help='show verbose information')

    args = parser.parse_args()

    if args.verbose:
        print("[Verbose] arguments: %s" % args)

    current_dir = os.getcwd()
    output_dict = {}

    # http://stackoverflow.com/questions/1592925/decoding-mac-os-text-in-python
    with codecs.open(args.linkmap_path, 'r', 'mac-roman') as f:
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
    for line in object_files_list:
        part_list = line.split("]")
        file_id = part_list[0].strip("[ ")
        file_name = os.path.basename(part_list[1]).strip()

        if file_name.find("(") != -1:
            library_name = file_name.split("(")[0]
            # 暂时注释掉这里，因为没有.a后缀不一定是framework
            """
            if not library_name.endswith(".a"):
                library_name += ".framework"
            """
            object_file_name = file_name.split("(")[1].strip(")")
            object_files_dict[int(file_id)] = object_file_name

            if library_name in object_library_dict:
                temp_list = object_library_dict[library_name]
                temp_list.append(object_file_name)
                object_library_dict[library_name] = temp_list
            else:
                object_library_dict[library_name] = [object_file_name]
        else:
            object_files_dict[int(file_id)] = file_name
            if file_name.endswith(".o"):
                if "main project" in object_library_dict:
                    temp_list = object_library_dict["main project"]
                    temp_list.append(file_name)
                    object_library_dict["main project"] = temp_list
                else:
                    object_library_dict["main project"] = [file_name]
            else:
                object_library_dict[file_name] = []

    # dump_object(object_files_dict)
    # dump_object(object_library_dict)

    if args.debug:
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
    if args.debug:
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
        # dump_object("%s size: %s" % (library_name, humansize(library_size)))
        module_dict[library_name + ".size"] = int(library_size)

    output_dict["Module"] = module_dict

    if (args.json is False) and (args.level == [1] or args.level == [2] or args.level == [3]):
        # Note: entering level 1
        library_dict = output_dict['Module']
        all_library_keys = library_dict.keys()
        filtered_library_keys = [i for i in all_library_keys if not i.endswith('.size')]

        def compare_by_library_size(x, y):
            x_size = library_dict[x + ".size"]
            y_size = library_dict[y + ".size"]
            if x_size > y_size:
                return 1 if not args.descend else -1
            elif x_size < y_size:
                return -1 if not args.descend else 1
            else:
                return 0

        if args.sorted == 'size':
            filtered_library_keys.sort(compare_by_library_size)
        else:
            filtered_library_keys = sorted(filtered_library_keys)

        for library_name in filtered_library_keys:

            if (args.library is not None) and (library_name not in args.library):
                continue

            library_size = library_dict[library_name + '.size']
            if args.sorted == 'name':
                print('%s: %s' %
                      (library_name,
                       humansize(library_size) if args.readable_size else str(library_size) + ' Bytes')
                      )
            elif args.sorted == 'size':
                print('%s: %s' %
                      (humansize(library_size) if args.readable_size else str(library_size) + ' Bytes',
                       library_name)
                      )

            if args.level == [2] or args.level == [3]:
                # Note: entering level 2
                object_dict = library_dict[library_name]
                all_object_keys = object_dict.keys()
                filtered_object_keys = [i for i in all_object_keys if not i.endswith('.size')]

                def compare_by_object_size(x, y):
                    x_size = object_dict[x + ".size"] if x.endswith('.o') else object_dict[x]
                    y_size = object_dict[y + ".size"] if y.endswith('.o') else object_dict[y]

                    if x_size > y_size:
                        return 1 if not args.descend else -1
                    elif x_size < y_size:
                        return -1 if not args.descend else 1
                    else:
                        return 0

                if args.sorted == 'size':
                    filtered_object_keys.sort(compare_by_object_size)
                else:
                    filtered_object_keys = sorted(filtered_object_keys)

                for object_name in filtered_object_keys:

                    if (args.object is not None) and (object_name not in args.object):
                        continue

                    object_size = object_dict[object_name + '.size'] if object_name.endswith('.o') else object_dict[object_name]
                    if args.sorted == 'name':
                        print('  %s: %s' %
                              (object_name,
                               humansize(object_size) if args.readable_size else str(object_size) + ' Bytes')
                              )
                    elif args.sorted == 'size':
                        print('  %s: %s' %
                              (humansize(object_size) if args.readable_size else str(object_size) + ' Bytes',
                               object_name)
                              )

                    if args.level == [3]:
                        # Note: entering level 3
                        symbol_dict = object_dict[object_name]
                        all_symbol_keys = symbol_dict.keys()

                        def compare_by_symbol_size(x, y):
                            x_size = symbol_dict[x]
                            y_size = symbol_dict[y]

                            if x_size > y_size:
                                return 1 if not args.descend else -1
                            elif x_size < y_size:
                                return -1 if not args.descend else 1
                            else:
                                return 0

                        if args.sorted == 'size':
                            all_symbol_keys.sort(compare_by_symbol_size)
                        else:
                            all_symbol_keys = sorted(all_symbol_keys)

                        for symbol_name in all_symbol_keys:
                            symbol_size = symbol_dict[symbol_name]
                            if args.sorted == 'name':
                                print('    %s: %s' %
                                      (symbol_name,
                                       humansize(symbol_size) if args.readable_size else str(symbol_size) + ' Bytes')
                                      )
                            elif args.sorted == 'size':
                                print('    %s: %s' %
                                      (humansize(symbol_size) if args.readable_size else str(symbol_size) + ' Bytes',
                                       symbol_name)
                                      )
    elif (args.json is True) and (args.level == [1] or args.level == [2] or args.level == [3]):
        # Note: entering level 1
        library_dict = output_dict['Module']

        def sort_dict(input_dict):
            if args.sorted == 'name':
                input_dict = OrderedDict(sorted(input_dict.items(), reverse=args.descend))
            elif args.sorted == 'size':
                input_dict = OrderedDict(sorted(input_dict.items(), key=lambda x: x[1], reverse=args.descend))
            return input_dict

        if args.level == [1]:
            library_dict = {k: v for k, v in library_dict.iteritems() if k.endswith('.size')}
            library_dict = sort_dict(library_dict)
            print(json.dumps(library_dict))
        elif args.level == [2]:
            for library_name in library_dict:
                if not library_name.endswith('.size'):
                    filtered_dict = library_dict[library_name]
                    filtered_dict = {k: v for k, v in filtered_dict.iteritems() if not k.endswith('.o')}
                    library_dict[library_name] = sort_dict(filtered_dict)
            library_dict = sort_dict(library_dict)
            print(json.dumps(library_dict))
        elif args.level == [3]:
            for library_name in library_dict:
                if not library_name.endswith('.size'):
                    object_dict = library_dict[library_name]
                    for object_name in object_dict:
                        if object_name.endswith('.o'):
                            symbol_dict = library_dict[library_name][object_name]
                            library_dict[library_name][object_name] = sort_dict(symbol_dict)
                    library_dict[library_name] = sort_dict(object_dict)
            library_dict = sort_dict(library_dict)
            print(json.dumps(library_dict))

    if args.debug:
        dict_to_json_file(output_dict, os.path.join(current_dir, 'size_info.json'))

if __name__ == '__main__':
    sys.exit(main())
