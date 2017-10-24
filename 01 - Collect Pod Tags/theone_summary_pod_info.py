#!/usr/bin/env python
# -*- coding: utf-8 -*-

# History:
#   2016-11-12 wesley_chen new version of parsing Podfile.lock
#   01b,9Nov.2016,caonian   Parser Podfile.lock instead of OneTravelPods.rb
#   01a,30Oct.2016,caonian  Initial version
#
# Usage:
#   1. Place theone_summary_pod_info.py along with Podfile.lock inside the same folder
#   2. Type command as followings:
#       python theone_summary_pod_info.py <folder containing json file>
#   3. Xcode -> Run Script
#       python "$PROJECT_DIR/theone_summary_pod_info.py"
#
# 1、<project root>/Pods/ONEDebugKit_<xcworkspace name>/Pod/Assets/tag_summary.json
# 2、<project root>/Pods/ONEDebugKit/Pod/Assets/tag_summary.json
# 3、根目录

import os
import sys
import logging
import json
from collections import OrderedDict


def main():
    # configurations
    fixed_pod_name = "ONEDebugKit"

    script_dir = os.path.dirname(sys.argv[0])
    script_name = os.path.basename(__file__)
    current_dir = os.getcwd()
    target_file_path = str(current_dir)

    if len(sys.argv) < 2:
        logging.warning("try to get target_file_path")
        path_by_fixed = os.path.join(current_dir, "Pods/" + fixed_pod_name + "/Pod/Assets")
        path_by_xcworkspace = ""
        for file in os.listdir(current_dir):
            if file.endswith(".xcworkspace") and len(file.split(".")) == 2:
                xcworkspace_file_name = file.split(".")[0]
                path = ['Pods', fixed_pod_name + "_" + xcworkspace_file_name, 'Pod', 'Assets']
                path_by_xcworkspace = os.path.join(current_dir, *path)
                break
        if len(path_by_xcworkspace) and os.path.exists(path_by_xcworkspace):
            target_file_path = path_by_xcworkspace
        elif len(path_by_fixed) and os.path.exists(path_by_fixed):
            target_file_path = path_by_fixed
        else:
            target_file_path = str(current_dir)
    else:
        target_file_path = sys.argv[1]  # if specify a target folder path

    if os.path.isdir(target_file_path):
        target_file_path = os.path.join(target_file_path, 'tag_summary.json')

    logging.warning("folder of tag_summary.json is: %s" % target_file_path)
    target_folder_path = os.path.abspath(os.path.dirname(target_file_path))

    if not os.path.exists(target_folder_path):
        logging.warning("'%s' path is not exist!" % target_file_path)
        sys.exit(0)

    LOG_FILE = os.path.join(script_dir, '%s.log' % script_name.split('.')[0])
    logging.basicConfig(filename=LOG_FILE, level=logging.WARNING, format="%(asctime)s %(filename)s[line:%(lineno)d] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    # logging.basicConfig(level=logging.WARNING,format="%(asctime)s %(filename)s[line:%(lineno)d] %(message)s",datefmt="%Y-%m-%d %H:%M:%S")

    WORKSPACE = os.getenv('WORKSPACE')
    logging.warning("WORKSPACE is: %s" % WORKSPACE)

    if WORKSPACE:
        podfile_lock_file_path = os.path.join(WORKSPACE, 'Podfile.lock')
    else:
        podfile_lock_file_path = os.path.join(current_dir, 'Podfile.lock')

    logging.warning("Podfile.lock path: %s" % podfile_lock_file_path)

    if not os.path.exists(podfile_lock_file_path):
        logging.error("%s is not exist!" % podfile_lock_file_path)
        sys.exit(0)
    else:
        with open(podfile_lock_file_path) as f:
            file_content = f.read()
            f.close()
        # logging.warning("file_content: %s" % file_content)

        PODS_string = file_content[file_content.index("PODS:") + len("PODS:"): file_content.index("DEPENDENCIES:")]
        DEPENDENCIES_string = file_content[file_content.index("DEPENDENCIES:") + len("SPEC CHECKSUMS:") : file_content.index("EXTERNAL SOURCES:")]
        SPEC_CHECKSUMS_string = file_content[file_content.index("SPEC CHECKSUMS:") + len("SPEC CHECKSUMS:") : file_content.index("PODFILE CHECKSUM:")]
        COCOAPODS_string = file_content[file_content.index("COCOAPODS") :]

        # logging.warning("PODS_string: %s" % PODS_string)

        # 1. Begin parsing PODS section
        pod_dependency_list = PODS_string.splitlines()
        pod_dependency_list = filter(None, pod_dependency_list)
        # logging.warning("pod_dependency_list: %s" % pod_dependency_list)

        pod_dependency_dict = {} # format: { <pod name> : { "version" : "blah", "dependencies" : [ "pod name1", "pod name2" ] } }
        index = 0
        while index < len(pod_dependency_list):
            line = pod_dependency_list[index]
            if line.startswith("  - "):
                pod_name = line.strip(" -:").split(" ")[0]
                pod_version = line.strip(" -:").split(" ")[1].strip("()")

                pod_dependency_dict[pod_name] = {"version": pod_version}

                if line.endswith(":"):
                    next_index = index + 1
                    dependency_list = []
                    while next_index < len(pod_dependency_list):
                        next_line = pod_dependency_list[next_index]
                        if next_line.startswith("    - "):
                            dependency_list.append(next_line.strip(" -"))
                            next_index += 1
                        else:
                            break

                    index = next_index
                    if len(dependency_list):
                        pod_dependency_dict[pod_name]["dependencies"] = dependency_list
                else:
                    index += 1
        # logging.warning("pod_dependency_dict: %s" % pod_dependency_dict)

        # 2. Begin parsing SPEC_CHECKSUMS section
        podspec_name_list = SPEC_CHECKSUMS_string.splitlines()
        podspec_name_list = filter(None, podspec_name_list)  # remove all empty items if it's an empty string
        podspec_name_list = map(str.strip, podspec_name_list) # strip all items with whitespace
        podspec_name_list = [i.split(':')[0] for i in podspec_name_list] # get first item
        # logging.warning("podspec_name_list is: %s" % podspec_name_list)

        # 3. Begin parsing DEPENDENCIES section
        pod_source_list = DEPENDENCIES_string.splitlines()
        pod_source_list = filter(None, pod_source_list)
        pod_source_list = [i.strip(" -") for i in pod_source_list]  # strip all items with " -"
        # logging.warning("pod_source_list is: %s" % pod_source_list)

        pod_source_dict = {} # format: { <pod name> : { "from" : "blah", "tag" : "blah", ... } }
        keys = ["from", "tag", "branch", "commit"]
        for pod_source in pod_source_list:

            if pod_source.find("(") != -1:
                pod_name = pod_source.split("(")[0].strip(" - ")

                source_dict = {}
                source_string = pod_source.split("(")[1].strip("()")
                # logging.warning("source_string is: %s" % source_string)

                if any((k in source_string for k in keys)):
                    source_dict = dict(item.split(" ") for item in source_string.split(", "))
                    source_dict = { k: v.strip("`") for k, v in source_dict.iteritems()}

                    # Check `from`
                    if "from" in source_dict.keys() and ".onepods" in source_dict["from"]:
                        version = source_dict["from"].split("/")[-1]
                        source_dict["tag"] = version
                    # logging.warning("dict is: %s" % source_dict)
                else:
                    source_dict["version"] = source_string

                pod_source_dict[pod_name] = source_dict
            else:
                pod_name = pod_source.strip(" - ")
                if pod_name in pod_dependency_dict.keys():
                    source_dict["version"] = pod_dependency_dict[pod_name]["version"]
                    pod_source_dict[pod_name] = source_dict

                # logging.warning("pod_name is: %s" % pod_name)

        # logging.warning("pod_source_dict is: %s" % pod_source_dict)

        lookup_pod_list = [item for item in podspec_name_list if item not in pod_source_dict.keys()]
        # logging.warning("lookup_pod_list is: %s" % lookup_pod_list)
        for pod_name in lookup_pod_list:
            if pod_name in pod_dependency_dict.keys():
                version = pod_dependency_dict[pod_name]["version"]
                pod_source_dict[pod_name] = { "version": version }

        # 4. Begin parsing COCOAPODS section
        cocoapods_list = COCOAPODS_string.splitlines()
        cocoapods_list = filter(None, cocoapods_list)  # remove all empty items if it's an empty string
        cocoapods_list = cocoapods_list[0].split(":")
        pod_source_dict["COCOAPODS"] = {"version": cocoapods_list[1].strip()}

        pod_source_dict = OrderedDict(sorted(pod_source_dict.items()))
        # logging.warning("pod_source_dict is: %s" % pod_source_dict)
        # logging.warning("json is: %s" % json.dumps(pod_source_dict))
        out_file = open(target_file_path, "w")
        out_file.writelines(json.dumps(pod_source_dict))
        out_file.close()

        return

if __name__ == '__main__':
    sys.exit(main())
