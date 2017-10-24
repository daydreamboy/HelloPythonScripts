#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Usage:
#
#
# Example:
# '/passport/user/resetPassword'
#
# Reference:
#   https://docs.python.org/2/library/httplib.html

import httplib
import urllib
import json

default_domain = 'passport.qatest.didichuxing.com'


def passport_api_request(path, params, method='POST', domain=default_domain, debug=False):
    params_full = dict(params)
    params_full.update({'role': 1})
    params_q = {'q': json.dumps(params_full)}

    params_encoded = urllib.urlencode(params_q)
    headers = {'Content-type': 'application/x-www-form-urlencoded', 'Accept': 'text/plain'}
    conn = httplib.HTTPConnection(domain)
    if debug:
        conn.set_debuglevel(1)
    conn.request(method, path, params_encoded, headers)
    response = conn.getresponse()
    if debug:
        print response.status, response.reason
    data = response.read()
    if debug:
        print data
    conn.close()

    return data

