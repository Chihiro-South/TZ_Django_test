#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# Time     : 2020-03-30 18:39
# Author   : Administrator
# File     : search_indexes.py
# Software : PyCharm
# Project  : TZ_Django_test

from haystack import indexes
from .models import News


class NewsIndex(indexes.SearchIndex, indexes.Indexable):
    """
    News索引数据模型类
    可以借用 hay_stack 借助 ES 来查询
    """
    #  主要进行关键字查询
    text = indexes.CharField(document=True, use_template=True)
    id = indexes.IntegerField(model_attr='id')
    title = indexes.CharField(model_attr='title')
    digest = indexes.CharField(model_attr='digest')
    content = indexes.CharField(model_attr='content')
    image_url = indexes.CharField(model_attr='image_url')

    def get_model(self):
        """
        返回建立索引的模型类
        """
        return News

    def index_queryset(self, using=None):
        """
        返回要建立索引的数据查询集
        """

        return self.get_model().objects.filter(is_delete=False)
