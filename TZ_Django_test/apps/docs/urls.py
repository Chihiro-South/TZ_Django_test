#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# Time     : 2020-04-01 20:28
# Author   : Smile辰
# File     : urls.py
# Software : PyCharm
# Project  : TZ_Django_test
from django.urls import path
from docs import views

app_name = 'docs'
urlpatterns = [
    path('',views.doc,name='docs'),
    path('download/<int:doc_id>/',views.DocDownload.as_view(),name='download')
]