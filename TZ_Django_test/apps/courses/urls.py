#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# Time     : 2020-04-01 20:41
# Author   : Smile辰
# File     : urls.py
# Software : PyCharm
# Project  : TZ_Django_test

from django.urls import path

from courses import views

app_name = 'courses'
urlpatterns = [
    path('', views.demo, name='course'),
    path('detail/<int:course_id>/', views.CourseDetail.as_view(), name='course_detail'),
]
