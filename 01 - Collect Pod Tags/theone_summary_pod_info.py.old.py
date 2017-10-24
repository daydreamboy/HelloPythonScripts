#!/usr/bin/env python
# -*- coding: utf-8 -*-

# modification history
# --------------------
# 01b,9Nov.2016,caonian   Parser Podfile.lock instead of OneTravelPods.rb
# 01a,30Oct.2016,caonian  Initial version
#

import os
import sys
import logging
import json
import commands
#from utility import FileHandler


def main():
    script_dir = os.path.dirname(sys.argv[0])
    script_name = os.path.basename(__file__)
    current_dir = os.getcwd()

    summary_pod_file = sys.argv[1]

    if os.path.isdir(summary_pod_file):
        summary_pod_file = os.path.join(summary_pod_file, 'tag_summary.json')
    logging.warning("summary_pod_file is: %s" % summary_pod_file)
    summary_pod_path = os.path.abspath(os.path.dirname(summary_pod_file))

    if not os.path.exists(summary_pod_path):
        logging.warning("'%s' path is not exist!" % summary_pod_file)
        sys.exit(0)

    LOG_FILE = os.path.join(script_dir, '%s.log' % script_name.split('.')[0])
    logging.basicConfig(filename=LOG_FILE, level=logging.WARNING,format="%(asctime)s %(filename)s[line:%(lineno)d] %(message)s",datefmt="%Y-%m-%d %H:%M:%S")
    # logging.basicConfig(level=logging.WARNING,format="%(asctime)s %(filename)s[line:%(lineno)d] %(message)s",datefmt="%Y-%m-%d %H:%M:%S")

    WORKSPACE = os.getenv('WORKSPACE')
    logging.warning("WORKSPACE is: %s" % WORKSPACE)

    if WORKSPACE:
        # pod_files = [os.path.join(WORKSPACE, 'Podfile'), os.path.join(WORKSPACE, 'OneTravelPods.rb')]
        pod_files = [os.path.join(WORKSPACE, 'Podfile.lock')]
    else:
        # pod_files = [os.path.join(current_dir, 'Podfile'), os.path.join(current_dir, 'OneTravelPods.rb')]
        pod_files = [os.path.join(current_dir, 'Podfile.lock')]

    for pod_file in pod_files:
        if not os.path.exists(pod_file):
            logging.error("%s is not exist!" % pod_file)
            sys.exit(0)
        else:
            logging.warning("pod file is: %s" % pod_file)
            pod_all_info_list = FileHandler().read_lines_from_file(pod_file)       
            DEPENDENCIES_index = pod_all_info_list.index("DEPENDENCIES:")
            EXTERNAL_SOURCES_index = pod_all_info_list.index("EXTERNAL SOURCES:")
            SPEC_CHECKSUMS_index = pod_all_info_list.index("SPEC CHECKSUMS:")
            DEPENDENCIES_pods = pod_all_info_list[DEPENDENCIES_index+1:EXTERNAL_SOURCES_index]
            pod_data = {}

            depenencies_pod_data = {}
            for depenencies_pod in DEPENDENCIES_pods:
                depenencies_pod_name = depenencies_pod.split("(")[0].split(' ')[1].strip()
                depenencies_pod_data[depenencies_pod_name] = depenencies_pod

            for spec_pod_index in range(SPEC_CHECKSUMS_index+1, len(pod_all_info_list)-2):
                spec_pod_info = pod_all_info_list[spec_pod_index]
                pod_name = spec_pod_info.split(":")[0].strip()

                if pod_name in depenencies_pod_data.keys():
                    depenencies_pod = depenencies_pod_data[pod_name]
                    if depenencies_pod.find("from") != -1:
                        pod_from = depenencies_pod.split("from")[1].split(",")[0].replace("`", "").replace(",", "").replace(")", "").strip()
                    else:
                        pod_from = ""

                    if pod_from.find(".onepods") != -1:
                        pod_tag = pod_from.split("/")[-1].split()
                    elif depenencies_pod.find("tag") != -1:
                        pod_tag = depenencies_pod.split("tag")[-1].replace("`", "").replace(")", "").strip()
                    else:
                        pod_tag = ""

                    if depenencies_pod.find("branch") != -1:
                        pod_branch = depenencies_pod.split("branch")[-1].replace("`", "").replace(")", "").strip()
                    else:
                        pod_branch = ""

                    if depenencies_pod.find("commit") != -1:
                        pod_commit = depenencies_pod.split("commit")[-1].replace("`", "").replace(")", "").strip()
                    else:
                        pod_commit = ""

                    if depenencies_pod.find("from") == -1 and depenencies_pod.find("(") != -1:
                        pod_version = depenencies_pod.split("(")[-1].replace("(", "").replace(")", "").strip()
                    elif depenencies_pod.find("from") == -1 and depenencies_pod.find("(") == -1:
                        st, pod_name_version = commands.getstatusoutput('grep ^"  - %s (" %s' % (pod_name, pod_file))
                        pod_version = pod_name_version.split("(")[-1].split(")")[0].strip()
                    else:
                        pod_version = ""
                else:
                    pod_from = ""
                    pod_tag = ""
                    pod_branch = ""
                    pod_commit = ""
                    st, pod_name_version = commands.getstatusoutput('grep ^"  - %s (" %s' % (pod_name, pod_file))
                    if not pod_name_version:
                        pod_version = pod_name_version.split("(")[-1].split(")")[0].strip()
                    else:
                        pod_version = ""
                
                pod_data[pod_name] = {"from": pod_from, "tag": pod_tag, "branch": pod_branch, "commit": pod_commit, "version": pod_version}

            cocoapods_version = pod_all_info_list[-1].split("COCOAPODS:")[-1].strip()
            pod_data["COCOAPODS"] = {"from": "", "tag": "", "branch": "", "commit": "",
                                  "version": cocoapods_version}

    FileHandler().write_lines_to_file(summary_pod_file, json.dumps(pod_data), False)

    # for pod_file in pod_files:
    #     logging.warning("Podfile is: %s" % pod_file)
    #     with open(pod_file, "rb") as f:
    #         pod_data = {}
    #         for l in f.readlines():
    #             line = l.strip()
    #             if line and not line.startswith("#") and line.startswith("pod") or line.startswith("pod_one"):
    #                 pod_name = line.split(',')[0].replace('"', '').replace("'", '').replace('pod_one', '').replace('pod', '').strip()
    #                 if line.find(':git') != -1:
    #                     pod_git_path = line.split(":git")[1].split(',')[0].replace('=>', '').replace('"', '').replace("'", '').strip()
    #                 else:
    #                     pod_git_path = ""
    #
    #                 if line.find(':tag') != -1:
    #                     pod_tag = line.split(':tag')[1].split(',')[0].split(',')[0].replace('=>', '').replace('"', '').replace("'", '').strip()
    #                 else:
    #                     pod_tag = ""
    #
    #                 if line.find(':branch') != -1:
    #                     pod_branch = line.split(':branch')[1].split(',')[0].split(',')[0].replace('=>', '').replace('"', '').replace("'", '').strip()
    #                 else:
    #                     pod_branch = ""
    #
    #                 pod_data[pod_name] = {"tag": pod_tag, "branch": pod_branch, "git": pod_git_path}

    # FileHandler().write_lines_to_file(summary_pod_file, json.dumps(pod_data), False)


if __name__ == '__main__':
    sys.exit(main())