#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# Time     : 2020-04-02 18:19
# Author   : Smile辰
# File     : urls.py
# Software : PyCharm
# Project  : TZ_Django_test

from django.urls import path
from . import views

app_name = 'admin'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),  # 将这条路由命名为index
    path('tags/', views.TagsManageView.as_view(), name='tags'),
    path('tags/<int:tag_id>/',views.TagsManageView.as_view(), name='tags_manage'),

    path('hotnews/', views.HotNewsManageView.as_view(), name='hotnews_manage'),
    path('hotnews/<int:hotnews_id>/', views.HotNewsDeleteView.as_view(), name='hotnews_delete'),
    path('hotnews/add/', views.HotNewsAddView.as_view(), name='hotnews_add'),
    path('tags/<int:tag_id>/news/', views.NewsByTagIdView.as_view(), name='news_by_tagid'),

    path('news/', views.NewsManage.as_view(), name='news_manage'),
    path('news/<int:news_id>/', views.NewsEditView.as_view(), name='news_edit'),
    path('news/pub/', views.NewsPubView.as_view(), name='news_pub'),
    path('news/images/', views.NewsUploadImage.as_view(), name='upload_image'),
    path('token/', views.UploadToken.as_view(), name='upload_token'),


    path('banners/', views.BannerManageView.as_view(), name='banners_manage'),
    path('banners/<int:banner_id>/', views.BannerEditView.as_view(), name='banners_edit'),
    path('banners/add/', views.BannerAddView.as_view(), name='banners_add'),

    path('docs/', views.DocsManageView.as_view(), name='docs_manage'),
    path('docs/<int:doc_id>/', views.DocsEditView.as_view(), name='docs_edit'),
    path('docs/pub/', views.DocsPubView.as_view(), name='docs_pub'),
    path('docs/files/', views.DocsUploadFile.as_view(), name='upload_text'),

    path('courses/', views.CoursesManageView.as_view(), name='courses_manage'),
    path('courses/<int:course_id>/', views.CoursesEditView.as_view(), name='courses_edit'),
    path('courses/pub/', views.CoursesPubView.as_view(), name='courses_pub'),
]
