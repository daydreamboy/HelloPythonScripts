#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Usage:
#   ./passport_user_update.py <prefix> <cell> [range_start] [range_end]
# Example:
#   ./passport_user_update.py +44 7000000000
#   ./passport_user_update.py +44 70000000XX 30 40
# curl command:
#   curl -X POST -d "q={\"country_id\":\"%2B44\",\"cell\":\"7000000000\",\"role\":1,\"channel\":\"1\"}"
#


import sys
import logging
import json
import time
from subprocess import call


def main():
    args_list = sys.argv
    if len(args_list) < 3:
        logging.warning("Usage: ./passport_user_update.py <countryCode> <phone number>")
        exit(0)

    # fixed parameters
    url_domain = "passport.qatest.didichuxing.com/passport/user/update"
    country_code = args_list[1].replace('+', '%2B')
    phone_number = args_list[2]
    command_list = ['curl', '-X', 'POST', '-d']  # ['curl', '--proxy', 'localhost:8888', '-X', 'POST', '-d']

    if phone_number.find('X') == -1:
        command_line = list(command_list)

        q_dict = {"country_id": country_code, "cell": phone_number, "role": 1, "channel": "1"}
        json_string = json.dumps(q_dict, separators=(',', ':'))
        json_string = json_string.replace('"', r'\"')
        q_string = '"' + "q=" + json_string + '"'
        command_line.append(q_string)
        command_line.append(url_domain)

        logging.warning("command_line_string: %s" % " ".join(command_line))
        call(command_line)
    else:
        if len(args_list) < 5:
            logging.warning("Error: missing arguments")
            logging.warning("Usage:\n\t ./passport_user_update.py +44 70000000XX 30 40")
            exit(0)

        start = int(args_list[3])
        end = int(args_list[4])

        phone_prefix = phone_number.replace('X', '')
        i = start
        while i <= end:
            command_line = list(command_list)
            cell = phone_prefix + str(i)
            q_dict = {"country_id": country_code, "cell": cell, "role": 1, "channel": "1"}
            json_string = json.dumps(q_dict, separators=(',', ':'))
            json_string = json_string.replace('"', r'\"')
            q_string = '"' + "q=" + json_string + '"'
            command_line.append(q_string)
            command_line.append(url_domain)
            logging.warning("command_line_string: %s" % " ".join(command_line))
            i += 1
            call(command_line)
            time.sleep(2)


if __name__ == '__main__':
    sys.exit(main())
