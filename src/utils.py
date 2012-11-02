#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 smallevilbeast
#
# Author:     smallevilbeast <houshao55@gmail.com>
# Maintainer: smallevilbeast <houshao55@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import time
import string
import urllib
import hashlib
import random

try:
    import simplejson as json
except ImportError:    
    import json

from xdg_support import get_cache_file

def timestamp():
    return int(time.time() * 1000)

def get_random_t():
    return random.random()

def radix(n, base=36):
    digits = string.digits + string.lowercase
    def short_div(n, acc=list()):
        q, r = divmod(n, base)
        return [r] + acc if q == 0 else short_div(q, [r] + acc)
    return ''.join(digits[i] for i in short_div(n))

def timechecksum():
    return radix(timestamp())

def quote(s):
    if isinstance(s, unicode):
        s = s.encode("gbk")
    else:    
        s = unicode(s, "utf-8").encode("gbk")
    return urllib.quote(s)    

def unquote(s):
    return urllib.unquote(s)

def get_cookie_file(username):
    return get_cache_file(hashlib.md5(username).hexdigest())


def parser_json(raw):
    try:
        data = json.loads(raw)
    except:    
        try:
            data = eval(raw, type("Dummy", (dict,), dict(__getitem__=lambda s,n: n))())
        except:    
            data = {}
    return data    
