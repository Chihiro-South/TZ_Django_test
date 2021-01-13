#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# Time     : 2020-04-03 18:37
# Author   : Smile辰
# File     : forms.py
# Software : PyCharm
# Project  : TZ_Django_test

from django import forms
from news.models import News, Tag


class NewsPubForm(forms.ModelForm):

    image_url = forms.URLField(label='文章图片url',
                               error_messages={"required": "文章图片url不能为空"})

    tag = forms.ModelChoiceField(queryset=Tag.objects.only('id').filter(is_delete=False),
                                 error_messages={"required": "文章标签id不能为空", "invalid_choice": "文章标签id不存在", }
                                 )

    class Meta: # 元数据信息
        # 指定那个数据库模型来创建表单
        model = News()  # 与数据库模型关联

        # fields = ['title', 'author', 'digest', 'content', 'image_url', 'tag']
        fields = ['title', 'digest', 'content', 'image_url', 'tag']

        error_messages = {
            'title': {
                'max_length': "文章标题长度不能超过150",
                'min_length': "文章标题长度大于1",
                # 传入字符串为空和，传入为空格是有区别的
                'required': '文章标题不能为空',
            },
            'digest': {
                'max_length': "文章摘要长度不能超过200",
                'min_length': "文章标题长度大于1",
                'required': '文章摘要不能为空',
            },
            'content': {
                'required': '文章内容不能为空',
            },
            # 'author': {
            #     'required': '作者不能为空',
            # },
        }


class DocsPubForm(forms.ModelForm):
    class Meta:
        pass


class CoursesPubForm(forms.ModelForm):
    class Meta:

        pass
