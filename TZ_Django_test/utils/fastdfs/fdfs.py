#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# Time     : 2020-04-03 19:59
# Author   : Smile辰
# File     : fdfs.py
# Software : PyCharm
# Project  : TZ_Django_test

from fdfs_client.client import Fdfs_client

# 指定fdfs客户端配置文件所在路径
from TZ_Django_test.settings.dev import FDFS_CLIENT_CONF

FDFS_Client = Fdfs_client(FDFS_CLIENT_CONF)

if __name__ == '__main__':
    try:
        # 此处指定图片路径上传的，知道文件后缀 upload_by_filename()
        ret = FDFS_Client.upload_by_filename('media/captcha.png')
    except Exception as e:
        print("fdfs测试异常：{}".format(e))
    else:
        print(ret)
