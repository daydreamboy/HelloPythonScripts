#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Usage:
#
#
# Example:
# '/passport/user/resetPassword'
#


from PassportRequest import *
import sys
import time


def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--path', default='/', type=str, nargs=1, help='the path of default test domain')
    # parser.add_argument('--params', type=dict, nargs='?', help='the parameter of http request')
    #
    # args = parser.parse_args()

    cell = 13700002011
    while cell <= 13700002222:
        print cell
        data = passport_api_request('/passport/user/resetPassword', {'cell': str(cell), 'password': '123456'}, debug=True)
        # print data, cell
        cell += 1
        time.sleep(1)

if __name__ == '__main__':
    sys.exit(main())
