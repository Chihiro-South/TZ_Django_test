#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# Time     : 2020-04-02 19:57
# Author   : Smile辰
# File     : json_fun.py
# Software : PyCharm
# Project  : TZ_Django_test
from django.http import JsonResponse

from TZ_Django_test.utils.res_code import Code


def to_json_data(errno=Code.OK, errmsg='', data=None, **kwargs):
    json_dict = {'errno': errno, 'errmsg': errmsg, 'data': data}
    if kwargs:
        json_dict.update(kwargs)
    return JsonResponse(json_dict)
